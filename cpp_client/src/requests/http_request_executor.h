#pragma once

#include <optional>
#include <QObject>
#include <QString>
#include <QUrl>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QTimer>

class HttpRequestExecutor: public QObject
{
    Q_OBJECT

public:
    enum class ReqMethod { GET, POST, PUT, DELETE };
    const char* methodName(ReqMethod mtd);

    struct Error : public std::exception
    {
        QString message;
        int code {-1};
        QJsonValue details;

        Error(QString message, int code = -1, QJsonValue details = QJsonValue())
            : message(std::move(message))
            , code(code)
            , details(std::move(details))
        {}

        virtual ~Error() = default;
        const char* what() const noexcept override
        {
            return "[HttpRequestExecutor] Failed to make request";
        }
        void log() const;
    };

    explicit HttpRequestExecutor(const QString& base_url = "", QObject* parent = nullptr);
    ~HttpRequestExecutor();

    QJsonObject makeRequest(
            const QString& endpoint,
            ReqMethod mtd,
            const QJsonObject& body = QJsonObject(),
            const QVariantMap& params = QVariantMap(),
            bool logError = false);

    QJsonObject get(
            const QString& endpoint,
            const QVariantMap& params = QVariantMap(),
            bool logError = false)
    {
        return makeRequest(endpoint, ReqMethod::GET, QJsonObject(), params, logError);
    }

    QJsonObject post(
            const QString& endpoint,
            const QJsonObject& body,
            const QVariantMap& params = QVariantMap(),
            bool logError = false)
    {
        return makeRequest(endpoint, ReqMethod::POST, body, params, logError);
    }

    QJsonObject del(
            const QString& endpoint,
            const QVariantMap& params = QVariantMap(),
            bool logError = false)
    {
        return makeRequest(endpoint, ReqMethod::DELETE, QJsonObject(), params, logError);
    }

    QJsonObject put(
            const QString& endpoint,
            const QJsonObject& body,
            const QVariantMap& params = QVariantMap(),
            bool logError = false)
    {
        return makeRequest(endpoint, ReqMethod::PUT, body, params, logError);
    }

signals:
    void requestFinished();

private slots:
    void onReplyFinished();
    void onTimeout();

private:
    void makeSyncRequest(const QUrl& url, ReqMethod mtd, const QJsonObject& body = QJsonObject());
private:
    QString m_baseUrl;
    QJsonObject m_responseData;
    QNetworkAccessManager* m_networkManager {nullptr};
    QTimer* m_timeoutTimer {nullptr};
    QNetworkReply* m_currentReply {nullptr};
    bool m_requestSuccess {false};
    std::optional<Error> m_requestError {std::nullopt};

};

