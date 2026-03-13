#define VAR(x) #x" = " << (x)
#define PRINT_VAR(x) qDebug().nospace() << VAR(x) << "\n"

namespace
{
class FakeClass {};
void fakeFunction(FakeClass) {}
} //namespace
