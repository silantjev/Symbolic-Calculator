#include <iostream>
#include <QApplication>
#include <QDir>
#include <QMainWindow>

#include "log.h"
#include "requests/calc_http_requester.h"
#include "calc_client.h"
#include "utils/files.h"
#include "gui/minigui.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    Logger logger(true);
    static Logger* loggerPtr = &logger;
    qInstallMessageHandler([](auto... args) { loggerPtr->handle(args...); });

    QString url;
    int timeout {0};
    const bool confOK = readUrlFromConfig(url, timeout);
    if (!confOK)
    {
        url = QString();
        timeout = 0;
        qDebug() << "Failed to read config file. Using default configurations";
    }

    auto* client = new CalcClient(url, timeout, &app);

    /*
    client->clearAll();
    client->setExpr("y/7");
    client->setNewExpr(client->getExpr());
    client->setValue("y", "-9");
    client->delValue("y");
    client->setOption("digits", 3);
    QString sec = client->evaluate();
    qInfo() << "evaluation result:" << sec;
    client->setSEC(sec);
    qInfo() << "nice:" << client->getNice();
    qInfo() << "exp:" << client->getExpr();
    qInfo() << "SE:" << client->getSE();
    qInfo() << "SEC:" << client->getSEC();
    qInfo() << "variable names:" << client->getVarNames();
    qInfo() << "variables:" << client->getVariables(false);
    // qInfo() << "Explanations:" << client->getExplanations();
    // qInfo().noquote() << client->getHelpText();

    return 0;
    */
    MiniWin window(client);
    window.show();
    return app.exec();
    return 0;
}
