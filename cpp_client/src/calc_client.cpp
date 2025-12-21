#include "calc_client.h"
#include "requests/json_dump.h"

CalcClient::CalcClient(const QString& baseUrl, int timeout, QObject* parent)
    : CalcHttpRequester(baseUrl, timeout, parent)  
{
    m_data = CalcHttpRequester::get("get_state", {{"full", true}});
    qInfo() << "CalcClient connected and loaded data:" << shortJson(m_data);
}

//Сеттеры с запросом действия

QString CalcClient::setNewExpr(const QString& expr)
{
    QString error = CalcHttpRequester::post("set_new_expr", {{"expr", expr}});
    if (error.isEmpty())
    {
        qInfo() << "New expression set: expr =" << m_data["expr"];
        qInfo() << "and parsed to sympy-expression: SE =" << m_data["se"];
    }
    else
    {
        qCritical() << "Error while setting new expression:" << error;
    }

    // QString key = "digits";
    // QJsonObject optObj = m_data["options"].toObject();
    // qDebug() << "1:" << optObj.contains(key);
    // qDebug() << "2:" << (optObj.value(key).type() == QJsonValue::Double);
    // qDebug() << "2:" << optObj[key].isDouble();
    // qDebug() << "3:" << optObj[key].toInt();
    // qDebug() << "m_data" << m_data;

    return error;
}

//Сеттеры с простыми запросами

void CalcClient::setExpr(const QString& expr)
{
    m_data["expr"] = expr;
    QString error = CalcHttpRequester::put_state(); // no exception
    assert (error.isEmpty());
    qInfo() << "Expression set: expr =" << m_data["expr"];
}

QString CalcClient::setSE(const QString& expr)
{
    m_data["se"] = expr;
    QString error = CalcHttpRequester::put_state();
    if (error.isEmpty())
    {
        qInfo() << "Sympy-expression set: SE =" << m_data["se"];
    }
    else
    {
        qCritical() << "Error while setting SE:" << error;
    }
    return error;

}

void CalcClient::setSEC(const QString& expr)
{
    m_data["sec"] = expr;
    QString error = CalcHttpRequester::put_state(); // no exception
    assert (error.isEmpty());
    qInfo() << "Sympy-expression 'calculated' set: SEC =" << m_data["sec"];
}

QString CalcClient::setValue(const QString& variable, const QString& value)
{
    assert (m_data["values"].isObject());
    QJsonObject valObj = m_data["values"].toObject();
    valObj[variable] = value;
    m_data["values"] = valObj;
    QString error = CalcHttpRequester::put_state();
    if (error.isEmpty())
    {
        qInfo() << "Value of" << variable << "set to" << m_data["values"].toObject()[variable];
    }
    else
    {
        qCritical() << "Error while setting value of a variable:" << error;
    }
    return error;

}

bool CalcClient::setOption(const QString& key, const int value)
{
    assert (m_data["options"].isObject());
    QJsonObject optObj = m_data["options"].toObject();
    if (optObj.contains(key) && optObj.value(key).type() == QJsonValue::Double && value == optObj[key].toInt())
    {
        qDebug() << "Trying to set the same value" << value << "to option" << key;
        return true;
    }

    if (key <= 0)
    {
        qWarning().nospace() << "Wrong value of " << key << ". The value should be positive, but " << value << " was given\n";
        return false;
    }

    optObj[key] = value;
    m_data["options"] = optObj;
    QString error = CalcHttpRequester::put_state();
    if (!error.isEmpty())
    {
        qCritical() << "Error while setting option:" << error;
        return false;
    }

    qInfo() << "Option" << key << "set to value" << value;

    return true;
}

//Чистые геттеры
QString CalcClient::getNice()
{
    return m_data["nice"].toString();
}

QString CalcClient::getExpr()
{
    return m_data["expr"].toString();
}

QString CalcClient::getSE()
{
    return m_data["se"].toString();
}

QString CalcClient::getSEC()
{
    return m_data["sec"].toString();
}

QStringList CalcClient::getVarNames()
{
    return m_data["values"].toObject().keys();
}

QJsonObject CalcClient::getOptions()
{
    return m_data["options"].toObject();
}

QString CalcClient::getHelpText()
{
    return m_data["help_text"].toString();
}

QJsonObject CalcClient::getExplanations()
{
    return m_data["explanations"].toObject();
}

//Геттеры с запросами
QJsonObject CalcClient::getVariables(bool includeUnset)
{
    return CalcHttpRequester::get("get_variables", {{"include_unset", includeUnset}});
}

QString CalcClient::getCurrentValues()
{
    QJsonObject outJson = CalcHttpRequester::get("current_values");
    return outJson["expr"].toString();
}

//Запросы действий

void CalcClient::delAllValues()
{
    CalcHttpRequester::del("delete_all_values");
    qInfo() << "Values of all variables deleted";
}

void CalcClient::delValue(const QString& variable)
{
    CalcHttpRequester::del("delete_value", {{"var", variable}});
    qInfo() << "Values of all variable" << variable << "deleted";
}

QString CalcClient::evaluate()
{
    QJsonObject outJson = CalcHttpRequester::get("evaluate");
    return outJson["expr"].toString();
    
}
void CalcClient::clearAll()
{
    CalcHttpRequester::del("clear_all");
    qInfo() << "State cleared";
}
