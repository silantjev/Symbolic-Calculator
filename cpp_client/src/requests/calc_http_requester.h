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
protected:
    QJsonObject m_data;
private:
    // clang-uml: aggregate -
    HttpRequestExecutor* m_executor;

public:
    CalcHttpRequester(const QString& baseUrl, int timeout, QObject* parent);

    virtual ~CalcHttpRequester() = default;

    void logData();

    void update(const QJsonObject& newdata);

    QJsonObject get(const QString& endpoint, const QVariantMap& params = QVariantMap());

    QString put_state();

    QString post(const QString& endpoint, const QJsonObject& body);

    void del(const QString& endpoint, const QVariantMap& params = QVariantMap());

    void saveState(int sessionId = 0);
};

