#include <QNetworkRequest>
#include <QUrlQuery>
#include <QJsonDocument>
#include <QEventLoop>

#include "http_request_executor.h"
#include "utils/defaults.h"
#include "json_dump.h"

//Вспомогательные функции
void addParams(QUrl& url, const QVariantMap& params)
{
    QUrlQuery query;
    for (auto it = params.begin(); it != params.end(); ++it)
    {
        query.addQueryItem(it.key(), it.value().toString());
    }
    url.setQuery(query);
}

HttpRequestExecutor::HttpRequestExecutor(const QString& baseUrl,  int timeout, QObject* parent) 
    : QObject(parent)
    , m_baseUrl(baseUrl)
    , m_networkManager(new QNetworkAccessManager(this))
    , m_timeoutTimer(new QTimer(this))
{
    if (m_baseUrl.isEmpty())
        m_baseUrl = DEFAULT_URL;
    if (timeout <= 0)
        timeout = DEFAULT_TIMEOUT;
    
    m_timeoutTimer->setSingleShot(true);
    m_timeoutTimer->setInterval(timeout); // таймаут в миллисекундах
}

HttpRequestExecutor::~HttpRequestExecutor()
{
    if (m_currentReply)
    {
        m_currentReply->deleteLater();
    }
}

QJsonObject HttpRequestExecutor::makeRequest(const QString& endpoint, ReqMethod mtd, const QJsonObject& body, const QVariantMap& params, bool logError)
{
    const char* mtdName = methodName(mtd);
    QUrl url(m_baseUrl + "/" + endpoint);
    
    // Добавляем параметры запроса (если нужны)
    if (!params.isEmpty())
    {
        addParams(url, params);
    }

    qDebug().nospace() << "Making" << mtdName << "request " << url.toString() << "...";
    this->makeSyncRequest(url, mtd, body);

    if (m_requestError.has_value())
    {
        if (logError)
        {
            m_requestError.value().log();
        }
        throw m_requestError.value();
    }

    if (!m_requestSuccess)
    {
        throw std::runtime_error(std::string(mtdName) + " Request to url \"" + url.toString().toStdString() + "\" failed");
    }
    
    return m_responseData;
}

void HttpRequestExecutor::makeSyncRequest(const QUrl& url, ReqMethod mtd, const QJsonObject& body)
{
    //Разъединяем предыдущие соединения
    if (m_timeoutConnection)
    {
        disconnect(m_timeoutConnection);
    }
    if (m_replyConnection)
    {
        disconnect(m_replyConnection);
    }

    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    
    //Сбрасываем флаги состояния
    m_requestError = std::nullopt;
    m_requestSuccess = false;

    QJsonDocument doc(body);
    QByteArray data = doc.toJson();
    
    //Выполняем запрос
    switch (mtd)
    {
    case (ReqMethod::GET):
        m_currentReply = m_networkManager->get(request);
        break;
    case (ReqMethod::POST):
        m_currentReply = m_networkManager->post(request, data);
        break;
    case (ReqMethod::DELETE):
        m_currentReply = m_networkManager->deleteResource(request);
        break;
    case (ReqMethod::PUT):
        m_currentReply = m_networkManager->put(request, data);
        break;
    }

    //Подключаем обработчики
    m_replyConnection = connect(
        m_currentReply, SIGNAL(finished()),
        this, SLOT(onReplyFinished()));
    Q_ASSERT(m_replyConnection);

    m_timeoutConnection = connect(
        m_timeoutTimer, SIGNAL(timeout()),
        this, SLOT(onTimeout()));
    Q_ASSERT(m_timeoutConnection);
    
    m_timeoutTimer->start();
    
    // Ожидаем завершения запроса
    QEventLoop loop;
    const bool connOK = connect(
        this, SIGNAL(requestFinished()),
        &loop, SLOT(quit()));
    Q_ASSERT(connOK);
    loop.exec();
}

//Слоты

void HttpRequestExecutor::onReplyFinished()
{
    m_timeoutTimer->stop();
 
    if (!m_currentReply)
    {
        m_requestSuccess = false;
        emit requestFinished();
        return;
    }
    
    if (m_currentReply->error() == QNetworkReply::NoError)
    {
        QByteArray response = m_currentReply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        
        if (doc.isObject())
        {
            m_responseData = doc.object();
            m_requestSuccess = true;
        }
        else
        {
            qCritical() << "Error: Invalid JSON response\n";
            m_requestSuccess = false;
        }
    }
    else
    {
        QByteArray response = m_currentReply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        int errorCode = m_currentReply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
        QJsonObject json = doc.object();
        QJsonValue details;
        QString message = m_currentReply->errorString();
        if (json.contains("detail"))
        {
            details = json["detail"];
        }
        else
        {
            message += "\nResponse: ";
            message += jsonDump(json);
        }
        if (m_currentReply->error() == QNetworkReply::ConnectionRefusedError)
             message += "\nIt seems like service is not running — run api_service on the host " + m_baseUrl;

        m_requestError = Error(message, errorCode, details);
        m_requestSuccess = false;
    }
    
    m_currentReply->deleteLater();
    m_currentReply = nullptr;
    emit requestFinished();
}

void HttpRequestExecutor::onTimeout()
{
    if (m_currentReply)
    {
        m_currentReply->abort();
        qCritical().nospace() << "Connection to '" << m_baseUrl << "' failed: timeout\n";
    }
}

//Вспомогательные публичные методы
const char* HttpRequestExecutor::methodName(ReqMethod mtd)
{
    switch (mtd)
    {
    case (ReqMethod::GET):    return "GET";
    case (ReqMethod::POST):   return "POST";
    case (ReqMethod::PUT):    return "PUT";
    case (ReqMethod::DELETE): return "DELETE";
    default:                  return "";
    }
}

void HttpRequestExecutor::Error::log() const
{
    qCritical() << "\nStatus:" << code;
    qCritical().noquote() << message;
    if (!details.isNull())
        qCritical().noquote()  << "Response details:" << jsonDump(details);
    qCritical() << "";
}

