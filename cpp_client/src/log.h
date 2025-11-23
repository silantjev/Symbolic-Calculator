#pragma once
#include <iostream>
#include <QDateTime>
#include <QFile>
#include <QTextStream>
#include <QMessageLogContext>
#include <QDebug>

class Logger final
{
public:
    Logger(bool console=false, const QString filename = QString())
        : m_console(console)
        , m_filename(filename)
    {
    }

    void handle(QtMsgType type, const QMessageLogContext& context, const QString& msg)
    {
        QString levelText;
        bool toErr {false};
        switch (type)
        {
            case QtDebugMsg:
                levelText = "DEBUG";
                toErr = false;
                break;
            case QtInfoMsg:   
                levelText = "INFO";
                toErr = false;
                break;
            case QtWarningMsg:
                levelText = "WARNING";
                toErr = true;
                break;
            case QtCriticalMsg:
                levelText = "CRITICAL";
                toErr = true;
                break;
            case QtFatalMsg:
                levelText = "FATAL";
                toErr = true;
                break;
        }
        QString formattedMsg = QString("[%1] [%2] %3")
            .arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
            .arg(levelText)
            .arg(msg);

        if (m_console)
        {
            if (toErr)
            {
                std::cerr << msg.toStdString() << std::endl;
            }
            else
            {
                std::cout << msg.toStdString() << std::endl;
            }
        }

        
        if (m_filename.isEmpty())
            return;
        QFile file(m_filename);
        if (file.open(QIODevice::WriteOnly | QIODevice::Append))
        {
            QTextStream stream(&file);
            stream << formattedMsg << Qt::endl;
        }
    }

private:
    bool m_console {false};
    QString m_filename;
};
