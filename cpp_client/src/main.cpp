#include <iostream>
#include <QApplication>
#include <QDir>
#include <QMainWindow>

#include <log.h>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    Logger logger(true);
    static Logger* loggerPtr = &logger;
    qInstallMessageHandler([](auto... args) { loggerPtr->handle(args...); });
    qDebug() << "Debug string";
    qInfo() << "Info string";
    qWarning() << "Warning string";
    qCritical() << "Critical string";

    //Устанавливаем путь к плагинам относительно бинарника
    // QDir binDir(QCoreApplication::applicationDirPath());
    // QCoreApplication::addLibraryPath(binDir.absoluteFilePath("platforms"));

    QMainWindow window;
    window.show();
    return app.exec();
}
