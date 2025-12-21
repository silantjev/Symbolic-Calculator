
#include "calc_http_requester.h"

//Вспомогательная функция (используется также в классе наследнике)
QJsonObject shortJson(QJsonObject data)
{
    const QString keys [2] = {"help_text", "explanations"};
    for (const QString& key : keys)
    {
        if (data.contains(key))
            data[key] = "...";
    }
    return data;
}

CalcHttpRequester::CalcHttpRequester(const QString& baseUrl, int timeout, QObject* parent)
    : QObject(parent)
    , m_executor(new HttpRequestExecutor(baseUrl, timeout, this))
{
}

void CalcHttpRequester::update(const QJsonObject& newdata)
{
    for (const auto& key : newdata.keys())
    {
        m_data[key] = newdata[key];
    }
}

QJsonObject CalcHttpRequester::get(const QString& endpoint, const QVariantMap& params)
{
    try
    {
        return m_executor->get(QString("calc/") + endpoint, params);
    }
    catch (const HttpRequestExecutor::Error& err)
    {
        qCritical() << "Error while getting full sate";
        err.log();
        throw;
    }
    catch (const std::exception& err)
    {
        qCritical() << "Error while getting sate";
        throw;
    }
}

QString CalcHttpRequester::put_state()
{
    try
    {
        QJsonObject newdata = m_executor->put("calc/put_state", m_data);
        this->update(newdata);
        qDebug() << "CalcClient updated data:" << shortJson(m_data);
        return "";
    }
    catch (const HttpRequestExecutor::Error& err)
    {
        if (err.details.isObject())
        {
            QJsonObject detailsObj = err.details.toObject();
            if (detailsObj.contains("Error") && detailsObj["Error"].isString())
                return detailsObj["Error"].toString();
        }
        qCritical() << "Error while putting sate";
        err.log();
        throw;
    }
    catch (const std::exception& err)
    {
        qCritical() << "Error while putting sate";
        throw;
    }
}

QString CalcHttpRequester::post(const QString& endpoint, const QJsonObject& body)
{
    try
    {
        QJsonObject newdata = m_executor->post(QString("calc/") + endpoint, body);
        this->update(newdata);
        qDebug() << "CalcClient updated data:" << shortJson(m_data);
        return "";
    }
    catch (const HttpRequestExecutor::Error& err)
    {
        if (err.details.isObject())
        {
            QJsonObject detailsObj = err.details.toObject();
            if (detailsObj.contains("Error") && detailsObj["Error"].isString())
                return detailsObj["Error"].toString();
        }
        qCritical() << "Error while making POST request";
        err.log();
        throw;
    }
    catch (const std::exception& err)
    {
        qCritical() << "Error while making POST request";
        throw;
    }
}

void CalcHttpRequester::del(const QString& endpoint, const QVariantMap& params)
{
    try
    {
        QJsonObject newdata = m_executor->del(QString("calc/") + endpoint, params);
        this->update(newdata);
        qDebug() << "CalcClient updated data:" << shortJson(m_data);
    }
    catch (const HttpRequestExecutor::Error& err)
    {
        qCritical() << "Error while making DELETE request";
        err.log();
        throw;
    }
    catch (const std::exception& err)
    {
        qCritical() << "Error while making DELETE request";
        throw;
    }
}

void CalcHttpRequester::saveState(int sessionId)
{
    try
    {
        QJsonObject newdata = m_executor->post("calc/save_state", {{"session_id", sessionId}});
    }
    catch (const HttpRequestExecutor::Error& err)
    {
        qCritical() << "Error while saving state";
        err.log();
        throw;
    }
    catch (const std::exception& err)
    {
        qCritical() << "Error while saving state";
        throw;
    }
}
