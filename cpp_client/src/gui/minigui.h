#pragma once

#include <QDialog> 

#include "calc_client.h"

namespace SCalc
{
class QLE;
}

class MiniWin final : public QDialog
{
    Q_OBJECT

    CalcClient* m_calc {nullptr};
    QPushButton* m_btnParse {nullptr};
    QPushButton* m_btnEval {nullptr};
    QPushButton* m_btnUp1 {nullptr};
    QPushButton* m_btnUp2 {nullptr};
    SCalc::QLE* m_inputText {nullptr};
    SCalc::QLE* m_SEText {nullptr};
    SCalc::QLE* m_SECText {nullptr};

public:
    MiniWin(CalcClient* calc);

protected:
    void closeEvent(QCloseEvent* event) override;

public slots:
    void reject() override;
    
private slots:
    void parseDown();
    void evalDown();
    void seUp();
    void secUp();
};
