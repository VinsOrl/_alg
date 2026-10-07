"""Solve cos(x) = x with the iteration method.

The solution is the Dottie number (~0.7390851332). Two iterations x_{n+1} = g(x_n):
  1. Fixed point:  g(x) = cos(x)                        -> linear convergence, rate |g'(x*)| = sin(x*) ~ 0.674
  2. Newton:       g(x) = x - (x - cos x) / (1 + sin x) -> quadratic convergence, g'(x*) = 0
"""
import math


def iterate(g, x0, tol=1e-12, max_iter=1000, show=10):
    x = x0
    for i in range(1, max_iter + 1):
        try:
            x_new = g(x)
        except ZeroDivisionError:  # e.g. Newton at x = -pi/2, where 1 + sin(x) = 0
            raise RuntimeError(f'update rule divided by zero at x = {x}') from None
        if i <= show:
            print(f'  {i:3d}  x = {x_new:.12f}  |dx| = {abs(x_new - x):.2e}')
        if abs(x_new - x) < tol:
            return x_new, i
        x = x_new
    raise RuntimeError('did not converge')


fixed = lambda x: math.cos(x)
newton = lambda x: x - (x - math.cos(x)) / (1 + math.sin(x))

if __name__ == '__main__':
    for name, g in [('Fixed point  x = cos(x)', fixed), ('Newton', newton)]:
        print(name)
        x, steps = iterate(g, 1.0)
        print(f'  -> x = {x:.12f} after {steps} steps, cos(x) - x = {math.cos(x) - x:.1e}\n')
        assert abs(math.cos(x) - x) < 1e-10
