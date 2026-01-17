#include <QKeyEvent>
#include <QApplication>

#include "qt_classes.h"

using namespace SCalc;

QLE::QLE(const QString& contents, QWidget* parent)
    : QLineEdit(contents, parent)
{
}

void QLE::keyPressEvent(QKeyEvent* event)
{
    const int key = event->key();
    if (QApplication::keyboardModifiers() == Qt::AltModifier)
    {
        if (key == Qt::Key_A)
        {
            this->home(false);
            return;
        }
        if (key == Qt::Key_E)
        {
            this->end(false);
            return;
        }
    }

    QLineEdit::keyPressEvent(event);
}
