#include <QPushButton> 
#include <QMessageBox>

#include "gui/minigui.h"
#include "gui/qt_classes.h"


MiniWin::MiniWin(CalcClient* calc)
    : m_calc(calc)
{
    this->setWindowTitle("Symbolic calculator");
    this->resize(450, 300);

    //Field with input text
    m_inputText = new SCalc::QLE(m_calc->getExpr(), this);
    m_inputText->move(50, 20);
    m_inputText->resize(350, 25);
    m_inputText->selectAll();
    connect(m_inputText, &SCalc::QLE::returnPressed, this, &MiniWin::parseDown);

    m_btnParse = new QPushButton("↓ преобразовать", this);
    m_btnParse->move(70, 50);
    connect(m_btnParse, &QPushButton::clicked, this, &MiniWin::parseDown);

    m_btnUp1 = new QPushButton("↑ перебросить", this);
    m_btnUp1->move(250, 50);
    connect(m_btnUp1, &QPushButton::clicked, this, &MiniWin::seUp);

    //Field with SE text
    m_SEText = new SCalc::QLE(m_calc->getSE(), this);
    m_SEText->move(50, 80);
    m_SEText->resize(350, 25);
    connect(m_SEText, &SCalc::QLE::editingFinished, this, &MiniWin::evalDown);

    m_btnEval = new QPushButton("↓ вычислить", this);
    m_btnEval->move(70, 110);
    connect(m_btnEval, &QPushButton::clicked, this, &MiniWin::evalDown);

    m_btnUp2 = new QPushButton("↑ перебросить", this);
    m_btnUp2->move(250, 110);
    connect(m_btnUp2, &QPushButton::clicked, this, &MiniWin::secUp);

    //Field with SEC text
    m_SECText = new SCalc::QLE(m_calc->getSEC(), this);
    m_SECText->move(50, 140);
    m_SECText->resize(350, 25);
}

//override to save state
void MiniWin::closeEvent(QCloseEvent* event)
{
    m_calc->saveState();
    QDialog::closeEvent(event);
}

//override to save state
void MiniWin::reject()
{
    m_calc->saveState();
    QDialog::reject();
}

//Parse the input expression to 'se' and evaluate it to 'sec'
void MiniWin::parseDown()
{
    QString expr = m_inputText->text();
    if (m_calc->getExpr() == expr)
        return;

    m_calc->setExpr(expr);

    QString error = m_calc->setNewExpr(expr);

    if (!error.isEmpty())
    {
        QMessageBox::warning(this, "Warning", error);
        return;
    }
    m_SEText->setText(m_calc->getNice());
    this->evalDown();
}

//Evaluates 'se' to 'sec'
void MiniWin::evalDown()
{
    QString seNewText = m_SEText->text();
    if (m_calc->getSE() != seNewText)
    {
        QString error = m_calc->setSE(seNewText);
        if (!error.isEmpty())
        {
            QMessageBox::warning(this, "Warning", error);
            return;
        }
    }

    QString sec = m_calc->evaluate();
    if (sec.contains("zoo") || sec.contains("nan") || sec.contains("inf"))
    {
        QMessageBox::warning(this, "Warning", "Деление на ноль");
    }
    else
    {
        m_calc->setSEC(sec);
        m_SECText->setText(sec);
    }
}

//Put 'se' to the top line (input)
void MiniWin::seUp()
{
    QString expr = m_calc->getSE();
    m_calc->setExpr(expr);
    m_inputText->setText(expr);
}

//Put 'sec' to 'se'
void MiniWin::secUp()
{
    QString se = m_calc->getSEC();
    QString error = m_calc->setSE(se);
    if (!error.isEmpty())
    {
        QMessageBox::warning(this, "Warning", error);
        return;
    }
    m_SEText->setText(se);
}
