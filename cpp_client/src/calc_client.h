#pragma once
#include <QObject>
#include <QString>

#include "requests/calc_http_requester.h"


class CalcClient final : private CalcHttpRequester
{
public:
    CalcClient(const QString& baseUrl, QObject* parent);

    //Сеттеры с запросом действия
    QString setNewExpr(const QString& expr);

    //Сеттеры с простыми запросами
    void setExpr(const QString& expr);
    QString setSE(const QString& expr);
    void setSEC(const QString& expr);
    QString setValue(const QString& variable, const QString& value);
    bool setOption(const QString& key, int value);

    //Чистые геттеры
    QString getNice();
    QString getExpr();
    QString getSE();
    QString getSEC();
    QStringList getVarNames();
    QJsonObject getOptions();
    QString getHelpText();
    QJsonObject getExplanations();

    //Геттеры с запросами

    //Возвращает словарь с ключами "current" и "lines"
    QJsonObject getVariables(bool includeUnset = true);
    QString getCurrentValues();

    //Запросы действий
    void delAllValues();
    void delValue(const QString& variable);
    QString evaluate();
    void clearAll();
};

