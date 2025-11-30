#include <QDebug>
#include <QApplication>

#include "calc_http_requester.h"

class FalkeClass {};

void fakeFunction(FalkeClass) {}

int sample_main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    auto* requester = new CalcHttpRequester("", &app);

    QString error = requester->post("set_new_expr", {{"expr", "x/5"}});
    if (!error.isEmpty())
    {
        qCritical() << "POST Error" << error;
        return 1;
    }

    QString error2 = requester->put_state();
    if (!error2.isEmpty())
    {
        qCritical() << "PUT Error" << error2;
        return 1;
    }
    QJsonObject responseData = requester->get("get_state", {{"full", true}});
    
    QDebug debug = qDebug().nospace();
    debug << "HttpRequestExecutor connected and loaded data:\n";
    // for (auto it = responseData.begin(); it != responseData.end(); ++it)
    // {
        // debug << "\t" << it.key() << ": " << it.value() << ",\n";
    // }

    debug << "\nexpr: " << responseData["expr"];
    debug << "\nse: " << responseData["se"];
    debug << "\nsec: " << responseData["se"];
    debug << "\nnice: " << responseData["nice"];
    debug << "\nvalues: " << responseData["values"];
    debug << "\noptions: " << responseData["options"];
    debug << "\n" ;
    
    return 0;
}
