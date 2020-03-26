#include <stdio.h>
extern int func();

int main()
{
  int a=func();
  printf("%d\n",a);
  return 0;
}