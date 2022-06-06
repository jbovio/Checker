import maya.mel as mm
import maya.cmds as mc
import pymel.core as pm
import maya.OpenMaya as mom
import maya.api.OpenMaya as om


class Symmetry():

    def getPoints(self,  geo ):
        """
        Get points from  MDagpath mesh

        :return: MPointArray
        """

        sel = mom.MSelectionList()
        dag = mom.MDagPath()

        sel.add(geo)
        sel.getDagPath(0, dag)

        mesh = mom.MFnMesh(dag)

        vts = mom.MPointArray() 
        mesh.getPoints(vts, mom.MSpace.kWorld) # Set points in worlspace

        return vts


    def getClosestPoint(self, mayaMesh, pos=[0, 0, 0]):
        
        # using MVector type to represent position
        mVector = om.MVector(pos)  

        selectionList = om.MSelectionList()
        selectionList.add(mayaMesh)

        dPath = selectionList.getDagPath(0)
        mMesh = om.MFnMesh(dPath)

        ID = mMesh.getClosestPoint(om.MPoint(mVector), space=om.MSpace.kWorld)[1]  # getting closest face ID

        list = mc.ls(mc.polyListComponentConversion(mayaMesh + '.f[' + str(ID) + ']', ff=True, tv=True),
                       flatten=True)  # face's vertices list

        # setting vertex [0] as the closest one
        d = mVector - om.MVector(mc.xform(list[0], t=True, ws=True, q=True))
        smallestDist2 = d.x * d.x + d.y * d.y + d.z * d.z  # using distance squared to compare distance
        
        closest = list[0]

        # iterating from vertex [1]
        for i in range(1, len(list)):

            d = mVector - om.MVector(mc.xform(list[i], t=True, ws=True, q=True))
            d2 = d.x * d.x + d.y * d.y + d.z * d.z

            if d2 < smallestDist2:
                smallestDist2 = d2
                closest = list[i]

        return closest

    def checkSymmetry(self, sourceMesh, threshold=8, tolerance = 0.000001 ):

        """
        Compare each vertex on mesh useing world space ref points +X ( plane YZ ).

        :return:  bool indicating whether the shape is symmetric, list of points those not match with the source side. 
        
        """

        # MPointArray , collect mesh points 
        pts = self.getPoints( sourceMesh )

        # Maya progress bar
        gMainProgressBar = mm.eval('$tmp = $gMainProgressBar');
        # Set progress bar.
        pm.progressBar(gMainProgressBar, edit=True, beginProgress=True, isInterruptable=False,
                        status='This may take a few...', maxValue=pts.length())

        noSymPoints = []
        symmetryState = True

        # Iterate for each mesh point 
        for i in range(pts.length()):
    
            # Take all points in x positive as reference and comparte to the nearest point in the oposite side 
            if pts[i].x > 0.0 :
                
                # Query mirror X pos from source point.
                mirrorPos = [ ( pts[i].x * -1.0 ), pts[i].y, pts[i].z ]
                # mirrorPos = [ ( round( pts[i].x * -1.0 ), threshold ), round( pts[i].y, threshold), round( pts[i].z, threshold) ]


                # Get Closest point in mirror X 
                mirrorPoint = self.getClosestPoint( mayaMesh = sourceMesh, pos = mirrorPos )
                # Query nearest oposite point Id.
                oppositPtnId = int(mirrorPoint.partition("[")[-1].replace("]", ""))

                # Round point 
                oppositPos = [ round( pts[ oppositPtnId ].x , threshold) , round( pts[ oppositPtnId ].y, threshold) , round(pts[ oppositPtnId ].z, threshold ) ]

                # Min/Max value determine the margin of error
                minValue = [ x - tolerance for x in mirrorPos ]
                maxValue = [ x + tolerance for x in mirrorPos ]

                # compare point position X,Y,Z.

                if oppositPos[0] < minValue[0] or oppositPos[0] > maxValue[0]:
                    noSymPoints.append( i )

                if oppositPos[1] < minValue[1] or oppositPos[1] > maxValue[1]:
                    noSymPoints.append( i )

                if oppositPos[2] < minValue[2] or oppositPos[2] > maxValue[2]:
                    noSymPoints.append( i )

            pm.progressBar(gMainProgressBar, edit=True, step=1) # increase progress bar
        
        pm.progressBar(gMainProgressBar, edit=True, endProgress=True) # End progress bar


        if noSymPoints:
            noSymPoints = set(noSymPoints)
            symmetryState = False


        return [ symmetryState, noSymPoints ]


