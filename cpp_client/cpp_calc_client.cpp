#include <iostream>
#include <QNetworkRequest>
#include <QUrlQuery>
#include <QJsonDocument>
#include <QEventLoop>

#include "CalcClient.h"

constexpr const char* DEFAULT_URL = "http://127.0.0.1:8000";

CalcClient::CalcClient(const QString& baseUrl, QObject* parent) 
    : QObject(parent)
    , m_baseUrl(baseUrl)
    , m_networkManager(new QNetworkAccessManager(this))
    , m_timeoutTimer(new QTimer(this))
    , m_currentReply(nullptr)
    , m_requestCompleted(false)
    , m_requestSuccess(false)
{
    if (m_baseUrl.isEmpty())
        m_baseUrl = DEFAULT_URL;
    
    m_timeoutTimer->setSingleShot(true);
    m_timeoutTimer->setInterval(5000); // 5 секунд таймаут
    
    // Загружаем начальные данные
    try
    {
        m_responseData = this->get("get_state", QVariantMap{{"full", true}});
        
        std::cout << "CalcClient connected and loaded data ";
        for (auto it = m_responseData.begin(); it != m_responseData.end(); ++it)
        {
            std::cout << it.key().toStdString() << " ";
        }
        std::cout << std::endl;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Failed to initialize CalcClient: " << e.what() << std::endl;
        throw;
    }
}

CalcClient::~CalcClient()
{
    if (m_currentReply)
    {
        m_currentReply->deleteLater();
    }
}

QJsonObject CalcClient::get(const QString& endpoint, const QVariantMap& params)
{
    QUrl url(m_baseUrl + "/calc/" + endpoint);
    //Добавляем параметры запроса
    if (!params.isEmpty())'
    {
        QUrlQuery query;
        for (auto it = params.begin(); it != params.end(); ++it)
        {
            query.addQueryItem(it.key(), it.value().toString());
        }
        url.setQuery(query);
    }

    std::cout << "Making GET request to: " << url.toString().toStdString() << std::endl;
    this->makeSyncRequest(url);
    
    if (!m_requestSuccess)
    {
        throw std::runtime_error("Request failed");
    }
    
    return responseData;
}

void CalcClient::makeSyncRequest(const QUrl& url)
{
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    
    //Сбрасываем флаги состояния
    m_requestCompleted = false;
    m_requestSuccess = false;
    
    //Выполняем запрос
    m_currentReply = m_networkManager->get(request);

    //Подключаем обработчики
    connect(m_currentReply, &QNetworkReply::finished, this, &CalcClient::onReplyFinished);
    connect(m_timeoutTimer, &QTimer::timeout, this, &CalcClient::onTimeout);
    
    m_timeoutTimer->start();
    
    // Ожидаем завершения запроса
    QEventLoop loop;
    connect(this, &CalcClient::requestFinished, &loop, &QEventLoop::quit);
    loop.exec();
}

void CalcClient::onReplyFinished()
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
            responseData = doc.object();
            m_requestSuccess = true;
        }
        else
        {
            std::cerr << "Error: Invalid JSON response" << std::endl;
            m_requestSuccess = false;
        }
    }
    else
    {
        std::cerr << "HTTP Error: " << m_currentReply->errorString().toStdString() 
                  << " Status: " << m_currentReply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt() 
                  << std::endl;
        m_requestSuccess = false;
    }
    
    m_currentReply->deleteLater();
    m_currentReply = nullptr;
    m_requestCompleted = true;
    emit requestFinished();
}

void CalcClient::onTimeout()
{
    if (m_currentReply)
    {
        m_currentReply->abort();
        std::cerr << "Connection to '" << m_baseUrl.toStdString() << "' failed: timeout" << std::endl;
        throw std::runtime_error("Connection failed: run api_service");
    }
}
