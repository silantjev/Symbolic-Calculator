#include <QJsonObject>
#include <QJsonArray>
#include <QTextStream>

#include "json_dump.h"

static void dump2stream(const QJsonValue& value, QTextStream& stream, const QString currentIndent, const QString indentStr) 
{
    if (value.isObject())
    {
        QJsonObject obj = value.toObject();
        if (obj.isEmpty())
        {
            stream << currentIndent << "{}\n";
        }
        else
        {
            stream << "{";
            bool notFirst = false;
            for (auto it = obj.begin(); it != obj.end(); ++it)
            {
                if (notFirst)
                    stream << ",";
                stream << "\n" << currentIndent + indentStr << '"' << it.key() << "\": ";
                dump2stream(it.value(), stream, currentIndent + indentStr, indentStr);
                notFirst = true;
            }
            stream << "\n" << currentIndent << "}";
        }
    }
    else if (value.isArray())
    {
        QJsonArray arr = value.toArray();
        if (arr.isEmpty())
        {
            stream << currentIndent << "[]";
        }
        else
        {
            stream << "[";
            bool notFirst = false;
            for (auto item : arr)
            {
                if (notFirst)
                    stream << ",";
                stream << "\n" << currentIndent + indentStr;
                dump2stream(item, stream, currentIndent + indentStr, indentStr);
                notFirst = true;
            }
            stream << "\n" << currentIndent << "]";
        }
    }
    else
    {
        stream << value.toString();
    }
}

QString jsonDump(const QJsonValue& value, int indent) 
{
    QString result;
    QTextStream stream(&result);
    QString indentStr = QString(" ").repeated(indent);
    dump2stream(value, stream, "", indentStr);

    return result;
}
