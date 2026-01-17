#pragma once
#include <QJsonValue>
#include <QString>

QString jsonDump(const QJsonValue& value, int indent = 4);
