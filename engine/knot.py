"""Procedural 3D: a trefoil knot tube meshed as ASCII STL. GitHub renders it as a rotatable 3D model."""
import math
def v_sub(a, b): return [a[i] - b[i] for i in range(3)]
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a):
    l = math.sqrt(sum(x * x for x in a)) or 1; return [x / l for x in a]

def stl(segs=64, sides=8, r=0.42):
    def P(t): return [math.sin(t)+2*math.sin(2*t), math.cos(t)-2*math.cos(2*t), -math.sin(3*t)]
    def D1(t): return [math.cos(t)+4*math.cos(2*t), -math.sin(t)+4*math.sin(2*t), -3*math.cos(3*t)]
    def D2(t): return [-math.sin(t)-8*math.sin(2*t), -math.cos(t)+8*math.cos(2*t), 9*math.sin(3*t)]
    rings = []
    for i in range(segs):
        t = 2 * math.pi * i / segs
        T = norm(D1(t)); Bn = norm(cross(D1(t), D2(t))); N = cross(Bn, T); c = P(t)
        rings.append([[c[k] + r * (math.cos(2*math.pi*j/sides)*N[k] + math.sin(2*math.pi*j/sides)*Bn[k]) for k in range(3)] for j in range(sides)])
    o = ["solid trefoil"]
    def tri(a, b, c):
        n = norm(cross(v_sub(b, a), v_sub(c, a)))
        o.append("facet normal %.2f %.2f %.2f\nouter loop" % tuple(n))
        for p in (a, b, c): o.append("vertex %.2f %.2f %.2f" % tuple(p))
        o.append("endloop\nendfacet")
    for i in range(segs):
        a, b = rings[i], rings[(i + 1) % segs]
        for j in range(sides):
            j2 = (j + 1) % sides
            tri(a[j], b[j], b[j2]); tri(a[j], b[j2], a[j2])
    o.append("endsolid trefoil")
    return "\n".join(o), segs * sides * 2
