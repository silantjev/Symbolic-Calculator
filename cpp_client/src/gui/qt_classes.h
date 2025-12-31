#pragma once

#include <QLineEdit>

class QKeyEvent;
class QWidget;

namespace SCalc
{

class QLE final : public QLineEdit
{
public:
    QLE(const QString& contents, QWidget* parent);
protected:
    void keyPressEvent(QKeyEvent* event) override;
};

} // namespace SCalc
