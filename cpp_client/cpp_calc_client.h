#pragma once

#include <QObject>
#include <QString>
#include <QUrl>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QTimer>
#include <iostream>

class CalcClient : public QObject
{
    Q_OBJECT

public:
    explicit CalcClient(const QString& base_url = "", QObject* parent = nullptr);
    ~CalcClient();

    QJsonObject get(const QString& endpoint, const QVariantMap& params = QVariantMap());

signals:
    void requestFinished();

private slots:
    void onReplyFinished();
    void onTimeout();

private:
    void makeSyncRequest(const QUrl& url);
private:
    QString m_baseUrl;
    QNetworkAccessManager* m_networkManager;
    QTimer* m_timeoutTimer;
    QNetworkReply* m_currentReply;
    QJsonObject m_responseData;
    bool m_requestCompleted;
    bool m_requestSuccess;

};

