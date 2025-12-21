#define VAR(x) #x" = " << (x)
#define PRINT_VAR(x) qDebug().nospace() << VAR(x) << "\n"

namespace
{
class FalkeClass {};
void fakeFunction(FalkeClass) {}
} //namespace
