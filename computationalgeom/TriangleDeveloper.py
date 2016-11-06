#!/usr/bin/python


from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import WindowProperties

from panda3d.core import RenderModeAttrib, LineSegs
from panda3d.core import Vec3, Vec4, Point3
from panda3d.core import Geom, GeomNode, GeomVertexData, GeomTriangles, GeomVertexFormat, GeomVertexRewriter
from utilities import pandaHelperFuncs as PHF
import utils as utilities
from triangle import Triangle  # Unit test Triangle


class Developer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        winProps = WindowProperties()
        winProps.setTitle("Triangle and SimpleCircle Unittest")
        # base.win.requestProperties(winProps) (same as below e.g. self == base)
        self.win.requestProperties(winProps)


        # 1) create GeomVertexData
        frmt = GeomVertexFormat.getV3n3cp()
        vdata = GeomVertexData('triangle_developer', frmt, Geom.UHDynamic)

        # 2) create Writers/Rewriters (must all be created before any readers and readers are one-pass-temporary)
        vertex = GeomVertexRewriter(vdata, 'vertex')
        normal = GeomVertexRewriter(vdata, 'normal')
        color = GeomVertexRewriter(vdata, 'color')

        zUp = Vec3(0, 0, 1)
        wt = Vec4(1.0, 1.0, 1.0, 1.0)
        gr = Vec4(0.5, 0.5, 0.5, 1.0)

        # 3) write each column on the vertex data object (for speed, have a different writer for each column)
        def addPoint(x, y, z):
            vertex.addData3f(x, y, z)
            normal.addData3f(zUp)
            color.addData4f(wt)

        addPoint(0.0, 0.0, 0.0)
        addPoint(5.0, 0.0, 0.0)
        addPoint(0.0, 5.0, 0.0)
        addPoint(15.0, 15.0, 0.0)

        # 4) create a primitive and add the vertices via index (not truely associated with the actual vertex table, yet)
        tris = GeomTriangles(Geom.UHDynamic)
        t1 = Triangle(0, 1, 2, vdata, tris, vertex)
        t2 = Triangle(2, 1, 3, vdata, tris, vertex)
        c1 = t1.getCircumcircle()
        t1AsEnum = t1.asPointsEnum()
        r0 = (t1AsEnum.point0 - c1.center).length()
        r1 = (t1AsEnum.point1 - c1.center).length()
        r2 = (t1AsEnum.point2 - c1.center).length()
        assert abs(r0 - r2) < utilities.EPSILON and abs(r0 - r1) < utilities.EPSILON
        t2AsEnum = t2.asPointsEnum()
        c2 = t2.getCircumcircle()
        r0 = (t2AsEnum.point0 - c2.center).length()
        r1 = (t2AsEnum.point1 - c2.center).length()
        r2 = (t2AsEnum.point2 - c2.center).length()
        assert abs(r0 - r2) < utilities.EPSILON and abs(r0 - r1) < utilities.EPSILON

        assert t1.getAngleDeg0() == 90.0
        assert t1.getAngleDeg1() == t1.getAngleDeg2()

        oldInd0 = t1.pointIndex0
        oldInd1 = t1.pointIndex1
        oldInd2 = t1.pointIndex2
        t1.pointIndex0 = t1.pointIndex1
        t1.pointIndex1 = oldInd0
        assert t1.pointIndex0 == oldInd1
        assert t1.pointIndex1 == oldInd0
        assert t1.pointIndex0 != t1.pointIndex1
        t1.reverse()
        assert t1.pointIndex1 == oldInd2

        # 5.1) (adding to scene) create a Geom and add primitives of like base-type i.e. triangles and triangle strips
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        # 5.2) create a GeomNode to hold the Geom(s) and add the Geom(s)
        gn = GeomNode('gnode')
        gn.addGeom(geom)
        # 5.3) attache the node to the scene
        gnNodePath = render.attachNewNode(gn)

        # setup a wire frame
        wireNP = render.attachNewNode('wire')
        wireNP.setPos(0.0, 0.0, .1)
        wireNP.setColor(0.1, 0.1, 0.1, 1)
        wireNP.setRenderMode(RenderModeAttrib.MWireframe, .5, 0)
        gnNodePath.instanceTo(wireNP)

        # test and draw intersections and circles
        pt1 = Point3(0.0, 5.0, 0.0)
        pt2 = Point3(1.0, 5.0, 0.0)
        intersection = t2.getIntersectionsWithCircumcircle(pt1, pt2)
        circle = t2.getCircumcircle()
        cuts = 128
        border = circle.getBorder(cuts, closed=True)
        assert len(border) == cuts or (len(border) == cuts + 1 and border[0] == border[len(border) - 1])
        n = len(border)
        xMid = yMid = 0
        for p in border:
            xMid += p.x
            yMid += p.y
        mid = Point3(xMid / n, yMid / n, border[0].z)
        assert mid.almostEqual(circle.center, 0.06)
        assert t2.isCcw()
        assert t1.containsPoint(c1.center) != t1.containsPoint(c1.center, includeEdges=False)

        circleSegs = LineSegs("circleLines")
        circleSegs.setColor(1.0, 0.0, 0.0, 1.0)
        for p in border:
            circleSegs.drawTo(*p)
        circleNode = circleSegs.create(False)
        circleNP = render.attachNewNode(circleNode)
        circleNP.setZ(-5)

        originSpot = LineSegs("intersection")
        originSpot.setColor(1.0, 0.0, 0.0, 1.0)
        originSpot.setThickness(10)
        for p in intersection:
            originSpot.drawTo(p)
        spotNode = originSpot.create(False)
        spotNP = render.attachNewNode(spotNode)
        circleNP.setZ(-0.75)

        # fix the camera rot/pos
        PHF.PanditorDisableMouseFunc()
        camera.setPos(0.0, 0.0, 50.0)
        camera.lookAt(c2.center)
        PHF.PanditorEnableMouseFunc()


        # TODO port the triangle-indices node func drawInds(...)
        #render.ls()


if __name__ == '__main__':
    print "Yep main"
    app = Developer()
    app.run()
