#pragma once

#include <QObject>
#include <QString>
#include <QJsonObject>

#include "http_request_executor.h"

//Вспомогательная функция (используется также в классе наследнике)
QJsonObject shortJson(QJsonObject data);

class CalcHttpRequester : public QObject
{
    Q_OBJECT

public:
    CalcHttpRequester(const QString& baseUrl, QObject* parent);

    virtual ~CalcHttpRequester() = default;

    void logData();

    void update(const QJsonObject& newdata);

    QJsonObject get(const QString& endpoint, const QVariantMap& params = QVariantMap());

    QString put_state();

    QString post(const QString& endpoint, const QJsonObject& body);

    void del(const QString& endpoint, const QVariantMap& params = QVariantMap());

    void saveState(int sessionId);

protected:
    QJsonObject m_data;
private:
    HttpRequestExecutor* m_executor;
};

