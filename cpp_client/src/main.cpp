#include <iostream>
#include <QApplication>
#include <QDir>
#include <QMainWindow>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    //Устанавливаем путь к плагинам относительно бинарника
    // QDir binDir(QCoreApplication::applicationDirPath());
    // QCoreApplication::addLibraryPath(binDir.absoluteFilePath("platforms"));

    QMainWindow window;
    window.show();
    return app.exec();
}
