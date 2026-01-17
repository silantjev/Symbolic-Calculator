#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>
#include <QDir>
#include <QFileInfo>

#include "utils/debug.h"
#include "utils/defaults.h"
#include "utils/files.h"

namespace
{
struct FileReader
{
    QFile file;

    explicit FileReader(const QString& path)
        : file(path)
    {
        const bool opened = file.open(QIODevice::ReadOnly | QIODevice::Text);
        Q_ASSERT(opened);
    }

    ~FileReader()
    {
        file.close();
    }
};
} // namespace

static QString getString(
    const QJsonObject& jsonObject,
    const QString& key,
    const QString& defaultValue = QString())
{
    if (jsonObject.contains(key))
    {
        const QJsonValue value = jsonObject[key];
        if (value.isString())
            return value.toString();
        qWarning() << "While parsing config: the value of" << key << "is not string";
    }
    return defaultValue;
}

static QString getUrlFromHostAndPort(const QJsonObject& jsonObject)
{
    QString host = DEFAULT_HOST;
    QString port = DEFAULT_PORT;
    const QString hostKey = "host";
    const QString portKey = "port";
    host = getString(jsonObject, hostKey, host);
    port = getString(jsonObject, portKey, port);
    return host + ":" + port;
}

bool readUrlFromConfig(QString& url, int& timeout)
{
    QDir dir = QFileInfo(__FILE__).dir();
    dir.cdUp(); // to src/
    dir.cdUp(); // to src/..
    QString configPath = dir.filePath(DEFAULT_CONFIG_NAME);
    qDebug() << "Looking for config at:" << configPath;

    if (!QFile::exists(configPath))
    {
        qWarning() << "Config file does not exist:" << configPath;
        return false;
    }
    
    FileReader reader(configPath);
    QByteArray data = reader.file.readAll();
    reader.file.close();
    const QJsonDocument jsonDoc = QJsonDocument::fromJson(data);
    if (!jsonDoc.isObject())
    {
        qWarning() << "Config" << configPath << "is not of JSON format";
        return false;
    }

    const QJsonObject jsonObject = jsonDoc.object();
    const QString urlKey = "url";
    const QString timeoutKey = "timeout";

    if (jsonObject.contains(urlKey))
    {
        url = getString(jsonObject, urlKey);
    }
    else
    {
        url = getUrlFromHostAndPort(jsonObject);
    }

    if (jsonObject.contains(timeoutKey))
    {
        QJsonValue timeoutValue = jsonObject[timeoutKey];
        if (timeoutValue.isDouble())
        {
            timeout = timeoutValue.toInt();
        }
        else
        {
            qWarning() << "timeout is not a number";
        }
    }
    return true;
}
