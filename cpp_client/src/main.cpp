#include <iostream>
#include <QApplication>
#include <QDir>
#include <QMainWindow>

#include "log.h"
#include "requests/calc_http_requester.h"
#include "calc_client.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    Logger logger(true);
    static Logger* loggerPtr = &logger;
    qInstallMessageHandler([](auto... args) { loggerPtr->handle(args...); });

    auto* client = new CalcClient("", &app);

    client->setNewExpr("x/6 - 6.7");

    return 0;
    auto* requester = new CalcHttpRequester("", &app);

    QString error = requester->post("set_new_expr", {{"expr", "x/5"}});
    if (!error.isEmpty())
    {
        qCritical() << "POST Error" << error;
        return 1;
    }


    return 0;
    // QMainWindow window;
    // window.show();
    // return app.exec();
}
