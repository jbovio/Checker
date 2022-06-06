import imp
from sys import prefix

from steamroller.tools.checker.lib import symmetry
imp.reload(symmetry)
sym = symmetry.Symmetry()

import maya.cmds as mc
import pymel.core as pm



class Model():

    def objectsWhitHistory( self, allowNodes = [] ):
        '''
        List all dag objects in scene and filter by if have construction history .

        :param allowNodes: type of nodes that are allowed in construction history, defined in the project configuration filters.
        return: list of tranform objects. 
        :rtype: string[]
        '''
        print ( 'ALLOW: ', allowNodes )

        objs_history = []
        nodes = []

        # Search history. 
        for node in mc.ls( dag = True ):
            history = mc.listHistory( node, pruneDagObjects = True ) or []

            if history:

                for x in history:
                    if not mc.nodeType( x ) in allowNodes :
                        nodes.append( node )
                        break
                    else:
                        pass

        print ( 'BIDE: ', nodes )
        # Filter transforms. 
        if nodes:
            for n in nodes:
                if mc.nodeType( n ) == 'transform':
                    objs_history.append( n )

        return objs_history

            
    def deleteHistory_check( self, *args ):
        """
        Notifies if there are objects with history in the scene.
        parameters are indicated in the list of projects

        :param args: piority = args[0][0], indicate if the check must be critical or warning.

        :return: (dic), { state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        """

        priority = args[0][0]
        allowNodes = args[0][1]
        
        objs_history = self.objectsWhitHistory( allowNodes = allowNodes )
        
        # Results 

        if objs_history:

            state = 2 # Error state
            note = 'Error, some objects still have construction history.'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects still have construction history.'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result        
   
    def deleteHistory_fix( self, *args ):
        """
        Delete object history.
        """

        # Query dag object that still have history
        obj_history = self.objectsWhitHistory()

        mc.undoInfo( openChunk = True )

        # Delete construction history.
        for n in obj_history:
            mc.delete( n, ch = True )

        mc.undoInfo( closeChunk = True )

    def deleteHistory_select( self, *args ):
        """
        Select the objects that have history.
        """
        # Query dag object that still have history
        obj_history = self.objectsWhitHistory()
        # Select objests 
        mc.select( obj_history )

    def freezeTransform( self, *args ):
        """
        Looking through all transfrom nodes in scene to list the nodes with transforms diferent then translate and rotate 
        (0, 0, 0) and scale ( 1,1,1).
        :Return: [ transform nodes ]
        """

        # List all camera transforms
        cams = [ mc.listRelatives( c, p=True )[0] for c in mc.ls( type = 'camera' ) ]

        # List all transforms nodes excluding cams.
        objs = [n for n in mc.ls( tr= True) if n not in cams ]

        noZeroNodes = []

        for n in objs:
            # Query transforms. 
            t = mc.getAttr( n + '.t' ) [ 0 ]
            r = mc.getAttr( n + '.r' ) [ 0 ]
            s = mc.getAttr( n + '.scale') [ 0 ]

            if t != (0, 0, 0):
                translate = False
            else:
                translate = True 

            if r != (0, 0, 0):
                rotate = False
            else:
                rotate = True 

            if s != (1, 1, 1):
                scale = False
            else:
                scale = True 
            
            if translate == False or rotate == False or scale == False:
                noZeroNodes.append( n )

        return noZeroNodes

    def freezeTransform_check( self, *args ):
        """
        Indicates if there are objects that are not found with freeze transformation.
        ( parameters are indicated in the list of projects )

        :param args: piority (args[0][0]), indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        """

        noZeroNodes = self.freezeTransform()

        # Results 
        priority = args[0][0]
        if  noZeroNodes:
            state = 2 # Error state
            note = 'Error, Some objects have not zero transforms: \n{0} '.format( noZeroNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, Some objects have not zero transforms: \n{0} '.format( noZeroNodes )


            return {'state': 3, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            return {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

    def freezeTransform_fix( self, *args ):
        """
        Freeze object transfromations.
        freezeTransform_fix is undoable.
        """

        noZeroNodes = self.freezeTransform()

        groupNode = []
        nodes = []

        mc.undoInfo( openChunk = True )

        for n in noZeroNodes:
            
            if not mc.listRelatives( n, ad = True, s = True ):
                groupNode.append( n )

            else:
                nodes.append( n )

        if groupNode:
            for gn in groupNode:
                # Query Childrens.
                children = mc.listRelatives( gn, ad = True )
                # Parent children under world 
                if children:
                    mc.parent( children, world=True )

                # zero pivot positon 
                mc.xform( gn, t = [ 0, 0, 0 ], ro = [ 0, 0, 0 ], ws = True )

                # Recreate hierarchy.
                mc.parent( children, gn )

        if nodes:
            for n in nodes:
                mc.makeIdentity( n, r = True, t = True, s = True, a = True ) 

        mc.undoInfo( closeChunk = True )

    def freezeTransform_select( self, *args ):
        """
        Select objects without freeze transformation.
        """
        noZeroNodes = self.freezeTransform()
        mc.select( noZeroNodes )

    def noCenterPvtNodes( self, *args):
        """
        The noCenterPvtNodes command returns the objects without center pivote in the scene.
        :return: string[]
        """
        # List all camera transforms
        cams = [ mc.listRelatives( c, p=True )[0] for c in mc.ls( type = 'camera' ) ]

        # List all transforms nodes excluding cams.
        transformNodes = [n for n in mc.ls( tr = True) if n not in cams ]

        noCenterPvt = []

        for n in transformNodes:
            pivot = mc.xform( n, pivots = True, ws = True, q = True ) 
            if not pivot == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]:
                noCenterPvt.append( n ) 

        return noCenterPvt
        
    def resetTransformsOrigin_check( self, *args ):
        """
        This command indicate if there objects with no world center pivot.

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dictionary 
        """

        noCenterPvt = self.noCenterPvtNodes()
        # Results 
        priority = args[0][0]
        if noCenterPvt:

            state = 2 # Error state
            note = 'Error, some objects do not have world center pivot.'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects do not have world center pivot.'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result   

    def resetTransformsOrigin_fix( self, *args ):
        """
        Center pivot for all objects in scene.
        """
        noCenterPvt = self.noCenterPvtNodes()

        if noCenterPvt:
            for n in noCenterPvt:
                mc.xform( n, pivots = [ 0, 0, 0 ], ws = True)  
    
    def resetTransformsOrigin_select( self, *args ):
        """
        Select objects without world center pivot.
        """
        noCenterPvt = self.noCenterPvtNodes()

        if noCenterPvt:
            mc.select( noCenterPvt )

    def objectsintersectionAxis( self, axis = 'x' ):
        """
        Query all object whose mesh shape are intersected by defined axis.

        :param axis: (str) indicates the axis ( x, y, z).

        :return: all shapes intersected by defined axis.
        :rtype: string[]
        """

        # List all mesh.
        mesh = pm.ls( type = 'mesh' )
        # Intersected mesh.
        intersectionObj = []

        # Query mesh bounding box and check if ther are intersected the defined axis.
        for m in mesh:

            meshParent = m.getParent()

            bbx = pm.exactWorldBoundingBox( m )
            
            centerX = (bbx[0] + bbx[3]) / 2.0
            centerY = (bbx[1] + bbx[4]) / 2.0
            centerZ = (bbx[2] + bbx[5]) / 2.0
            
            if axis == 'x':
                if ( bbx[0] + centerX ) < 0 and ( bbx[3] + centerX ) > 0:
                    intersectionObj.append( meshParent )
                else: 
                    pass

            if axis == 'y':
                if ( bbx[1] + centerY ) < 0 and ( bbx[4] + centerY ) > 0:
                    intersectionObj.append( meshParent )
                else: 
                    pass

            if axis == 'z':
                if ( bbx[2] + centerZ ) < 0 and ( bbx[5] + centerZ ) > 0:
                    intersectionObj.append( meshParent )
                else: 
                    pass


        return intersectionObj

    def symmetry_check( self, *args ):

        global noSymObjs 

        # Check worldspace symmetry on selection mesh. 
        # if there nothing selected the checker take all mesh intersect on X axis.

        axis = args[0][1]

        selection = pm.ls( sl = True )

        if selection:
            objs = []
            for x in selection:
                if pm.nodeType(x) == 'transform':
                    if x.getShape():
                        if pm.nodeType( x.getShape() ) == 'mesh':
                            objs.append(x)

        else:
            objs = self.objectsintersectionAxis()
            
        # Store no sym objects.
        noSymObjs = []
        onlyObjs = []

        if objs:

            for obj in objs:
                
                objName = obj.name()
                
                symResult = sym.checkSymmetry( sourceMesh = objName ) # Return [ sym status (bool), out os sym points id [list] ]

                if symResult[0] == False:
                    noSymObjs.append( [ obj, symResult[1] ] )
                    onlyObjs.append( obj )

        priority = args[0][0]
        if noSymObjs:
    
            state = 2 # Error state
            note = 'Error, the follow objects are not symmetry. \n'  + str( onlyObjs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects are not symmetry. \n'  + str( onlyObjs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok. ( Symmetry check only object intersect by ' + axis + 'axis. ) \n'  + str( objs )
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result     

    def symmetry_select( self, *args ):
        """
        Select the no symetrical objects in defined axis intersection.
        The axis is defined in the parameters of the check list. ( X axis as defalut )
        """
        # Select objects in X axis intersection that are no symmetry.
        
        mc.select( cl = True )

        for x in noSymObjs:
            pm.select( x[0], add = True )

    def noQuads( self ):
        """
        noQuads function select all mesh type in scene and look for faces that not have 4 sides

        :retrun: No quads face list.
        :rtype: string[]
        """

        noQuads = []

        mesh = mc.ls( type = 'mesh' )

        if mesh:

            mc.select( mesh ) # Select all mesh in scene.
            mc.polySelectConstraint( m = 3, sz = 2, t = 8 ) # Select all Quads.
            mc.InvertSelection() 
            noQuads = mc.ls( sl = True )
            # mc.select( cl = True ) 

        return noQuads

    def allQuads_check( self, *args ):
        """
        This command indicate if there noQuads face components in the scene.

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dictionary
        """
        
        noQuads = self.noQuads()
        mc.select( cl = True ) 

        priority = args[0][0]

        if noQuads:
            
            state = 2 # Error state
            note = 'Error, not all polygons are quads.'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, not all polygons are quads.'

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result  

    def allQuads_select( self, *args ):
        """
        Select all face components in scene that not have 4 sides.
        """
        self.noQuads()

    def nGons( self ):
        """
        search in all objects faces that are nGons.

        :retrun: nGons face list.
        :rtype: string[]
        """
        mc.select( mc.ls( type = 'mesh' ) ) # Select all mesh in scene.
        mc.polySelectConstraint( m=3, t=8, sz=3 ) # to get N-sided
        nGons = mc.ls( sl = True )
        mc.select( cl = True ) 
        
        return nGons

    def nGons_check( self, *args ):
        """
        This command indicate if there **nGons** face components in the scene.

        * fix button: available (  model.nGons_fix() ), undo: available.
        * extra button: label "Sel" ( model.nGons_extra() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dictionary
        """

        priority = args[0][0]

        nGons = self.nGons()

        if nGons:
            
            state = 2 # Error state
            note = 'Error, some geometries present N-Gons.'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some geometries present N-Gons.'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result  

    def nGons_select( self, *args ):
        """
        Select all nGons mesh components in scene.
        """
        nGons = self.nGons()
        mc.select( nGons )

    def nGons_fix( self, *args ):
        """
        Trangulate all nGons faces in scene.

        undo: available.
        """

        nGons = self.nGons() # Query all N-gons polygons in scene.

        mc.undoInfo( openChunk = True )

        # List diferent objects from nGons list.
        objs = [] 

        for obj in nGons:
            objName = obj.split('.')[0] # Extract obj name
            objs.append( objName )
            
        objs = set(objs)    

        mc.select( cl = True ) 

        for obj in objs:
            mc.select( cl = True ) 

            for f in nGons:  
                if (obj + '.') in f: # If object name exist in face id ( pSphere.f[x] ) add to selection. 
                    mc.select( f, add=True ) 

            mc.polyTriangulate( mc.ls(sl=True) )
            
        # Delete history 
        for n in objs:
            mc.delete( n, ch = True )

        mc.undoInfo( closeChunk = True )

    def nonManifoldGeo( self ):
        """
        This command find all **nonManifold** component in the scene.
        :return: List with face compoents.
        :rtype: string[]
        """

        # Query all mesh type in scene.
        mesh = mc.ls( type = 'mesh',  objectsOnly = True,  noIntermediate = True )

        # Get mesh parent. ( transform object )
        objs = []

        for m in mesh:
            parent = mc.listRelatives( m, p = True )[0]
            objs.append( parent )


        meshInfo = {}

        # Non mani fold edges.
        for obj in objs:
            meshInfo[ obj ] = {}
            foldEdge = mc.polyInfo( obj, nonManifoldEdges = True )

            laminaFace = mc.polyInfo( obj, laminaFaces = True )

            if foldEdge:
                meshInfo[ obj ][ 'foldEdge' ] =  foldEdge 

            if laminaFace:
                meshInfo[ obj ][ 'laminaFace' ] = foldEdge 


        return meshInfo

    def nonManifoldGeo_check( self, priority = int,  *args ):
        """
        This command indicate if there **nonManifold** face components in the scene.

        * fix button: none.
        * extra button: label "Sel" ( model.nonManifoldGeo_extra() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: dictionary.
        """

        polyInfo = self.nonManifoldGeo() 

        errorObjs = []
        onlyObjs = []

        for obj in polyInfo.keys():
            try:
                if polyInfo[ obj ][ 'foldEdge' ]:
                    errorObjs.append( [obj, polyInfo[ obj ][ 'foldEdge' ] ] )
                    onlyObjs.append( obj )
            except:
                pass

        if errorObjs:
            
            state = 2 # Error state
            note = 'Error, nonManifoldGeo: \n' + str( onlyObjs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, nonManifoldGeo: \n' + str( onlyObjs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def nonManifoldGeo_select( self, *args ):
        """
        Select all nonManifold faces component in scene.
        """
        polyInfo = self.nonManifoldGeo() 

        mc.select( cl = True )

        for obj in polyInfo.keys():
            if polyInfo[ obj ][ 'foldEdge' ]:
                mc.select( polyInfo[ obj ][ 'foldEdge' ], add = True )
                
    def laminaFace_check( self, priority = int, *args ):
        """
        This command indicate if there **laminaFace** components in the scene.

        * fix button: none.
        * extra button: label "Sel" ( model.laminaFace_extra() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        polyInfo = self.nonManifoldGeo() 

        errorObjs = []
        onlyObjs = []

        for obj in polyInfo.keys():
            try:
                if polyInfo[ obj ][ 'laminaFace' ]:
                    errorObjs.append( [obj, polyInfo[ obj ][ 'laminaFace' ] ] )
                    onlyObjs.append( obj )
            except:
                pass

        # 
        if errorObjs:
            
            state = 2 # Error state
            note = 'Error, laminaFace: \n' + str( onlyObjs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, laminaFace: \n' + str( onlyObjs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def laminaFace_select( self, *args ):
        """
        Select all "laminaFace" components in scene.
        """
        polyInfo = self.nonManifoldGeo() 

        mc.select( cl = True )

        for obj in polyInfo.keys():
            if polyInfo[ obj ][ 'laminaFace' ]:
                mc.select( polyInfo[ obj ][ 'laminaFace' ], add = True )
                
    def emptyGroups( self, *args ):
        """
        This function find all the transforms nodes those not have children in they hierarchy.

        :return: List of empty transforms nodes.
        :rtype: string[]
        """
        nodes = mc.ls( type='transform' )
        emptyNodes = []

        for n in nodes:
            if mc.listRelatives(n, ad=True):
                pass
            else:
                emptyNodes.append(n)

        return emptyNodes

    def emptyGroups_check(self, *args ):
        """
        This command indicate if there empty transforms nodes in the scene.

        * fix button: available (  model.emptyGroups_fix() ), undo: available.
        * extra button: label "Sel" ( model.emptyGroups_select() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        priority = args[0][0]

        emptyGrps = self.emptyGroups()

        if emptyGrps:
            state = 2 # Error state
            note = 'Error, empty groups: \n' + str( emptyGrps )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, empty groups: \n' + str( emptyGrps )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def emptyGroups_fix( self, *args ):
        """
        Delete all the transforms nodes those not have children in they hierarchy.
        undo: avaiable.
        """

        emptyGroups = self.emptyGroups()

        mc.undoInfo( openChunk = True )

        mc.lockNode( emptyGroups, l = False )
        mc.delete( emptyGroups )

        mc.undoInfo( closeChunk = True )

    def emptyGroups_select( self, *args ):
        """
        Select all the transforms nodes those not have children in they hierarchy.
        """
        emptyGroups = self.emptyGroups()

        mc.select( emptyGroups )

    def repeatNames( self ):

        """
        This function compare all transfroms nodes names and flag the repeat ones.
        :retunr: Transforms nodes with repeat names.
        :rtype: string[]
        """
        # List all transforms nodes 
        all = mc.ls( type = 'transform', l = True )

        # extract single node name. 
        names = []
        objs = []

        for x in all:
            # [ long name , name ]
            names.append( x.split( '|' )[ -1 ] )
            objs.append( x )


        repeatObjs = []
        i = 0
        for n in names:
            if names.count( n ) > 1:
                repeatObjs.append ( objs[ i ] )
            i = i + 1

        return repeatObjs

    def noIdenticalNames_check( self, *args ):
        """
        This command indicate if there no identical names per transform nodes in scene.

        * fix button: none.
        * extra button: label "Sel" ( model.noIdenticalNames_select() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        repeatNameObjs = self.repeatNames()

        if repeatNameObjs:
            state = 2 # Error state
            note = 'Error, no identical names: \n' + str( repeatNameObjs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, no identical names: \n' + str( repeatNameObjs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def noIdenticalNames_select( self, *args ):
        """
        Select transfrom nodes with no identical name.
        """
        objs = self.repeatNames()
        mc.select( objs )

    def noIdenticalShapeNames( self ):
        """
        Compare shape name with parent transform name if the shape name is no equal as transform plus "Shape" sufix
        returns a list with the shape.
        :returns: No match shape names. 
        :rtype: string[]
        """

        # List all shapes in scene.
        allShapes = mc.ls( s=True, l=True )

        # Filter shapes type.
        allowShapes = ['mesh', 'nurbsSurface']

        shapes = []
        noMatchShapes = []

        for s in allShapes:
            if mc.nodeType( s ) in allowShapes:
                shapes.append( s )

        for s in shapes:
            parent = mc.listRelatives( s, p = True, f = True )[0]
            pName = parent.split( '|')[-1]
            sName = s.split( '|')[-1]
            if not ( pName + 'Shape' ) == sName:
                noMatchShapes.append( s )

        return noMatchShapes

    def noIdenticalShapeNames_check( self, *args ):
        """
        This command indicate if there no match between transforms nodes name and shape name.

        * fix button: available (  model.noIdenticalShapeNames_fix() ), undo: available.
        * extra button: label "Sel" ( model.noIdenticalShapeNames_select() )

        :param args:  ( args[0][0] ) piority, indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[ 0 ][ 0 ]

        shapes = self.noIdenticalShapeNames()

        if shapes:
            state = 2 # Error state
            note = 'Error, no match shape name : \n' + str( shapes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, no match shape name : \n' + str( shapes )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def noIdenticalShapeNames_select( self, *args ):
        """
        Select objects whose shape name doesn't match with transform name.
        """
        shapes = self.noIdenticalShapeNames()
        mc.select( shapes )

    def noIdenticalShapeNames_fix( self, *args ):
        """
        Rename the shapes whose doesn't match with transform name.
        undo: avaiable.

        * example: nt.transform( *GEO_body* ), incorrect: nt.mesh( *GEO_body_upper_shape* ) correct: nt.mesh( *GEO_bodyShape* )
        """
    
        shapes = self.noIdenticalShapeNames()
        mc.undoInfo( openChunk = True )
        for s in shapes:
            parent = mc.listRelatives( s, p = True, f = True )[0]
            pName = parent.split( '|' )[-1]

            mc.rename(s, ( pName + 'Shape' ) )
        
        mc.undoInfo( closeChunk = True )

    def assetGroup( self, assetName = '', sufix = '_GRP' ):
        """
        Check if the asset main group exists if it does not create it.

        :return: transform node name. 
        :rtype: string
        """
        # assetName convention , first letter is upper case
        assetName = assetName[0].upper() + assetName[1:]

        # Check if asset group exists.
        if mc.objExists( assetName + sufix ):
            return ( assetName + sufix )
        else:
            assetGrp = mc.createNode( 'transform', n = assetName + sufix )
            return assetGrp

    def assemblyHierarchy( self, assetName = '' ):
        """
        Collect all objects that are not under the main asset group.

        :return: list of assemblies dag objects.
        :rtype: string[]
        """

        # Query main asset group.
        assetGrp = self.assetGroup( assetName = assetName )

        # List assemblies 
        assemblies = mc.ls( assemblies = True )

        # Remove cameras and main asset group. 
        removeNodes = [ 'persp', 'top', 'side', 'front', assetGrp ]

        for x in removeNodes:
            try:
                assemblies.remove( x )
            except:
                pass

        return assemblies

    def groupName_check( self, *args ):
        """
        This function indicates whether the containing groups are named correctly.
        
        naming covnetions:
        * First word capitalized. 
        * After a underscore "_" the next string need to be uppercase.
        * Group sufix ( _GRP )

        :param args: Arguments defined in the project list.  ( priority, assetName, prefix, sufix ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.
        :param assetName: args[0][1] , asset name.
        :param prefix: args[0][2] , The valid prefix for the groups if not defined the argument can be an empty string.
        :param sufix: args[0][3] , Rhe valid sufix for the groups if not defined the argument can be an empty string.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        assetName = args[0][1][0]
        prefix = args[0][1][1]
        sufix = args[0][1][2]

        assetGrp = self.assetGroup( assetName = assetName, sufix = sufix )

        incorrectNames = self.groupsName( parentNode = assetGrp, grpPrefix = prefix, grpSufix = sufix )

        if incorrectNames:
            state = 2 # Error state
            note = 'Error, This groups do not follow the naming conventions:  \n' + str( incorrectNames )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, This groups do not follow the naming conventions:  \n' + str( incorrectNames )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def groupName_fix( self, *args ):
        """
        This function fix the group names based in the defined nameing conventions.
        
        :param args: Are the defined arguments in the project list.  ( priority, assetName, prefix, sufix ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.
        :param assetName: args[0][1] , asset name.
        :param prefix: args[0][2] , The valid prefix for the groups if not defined the argument can be an empty string.
        :param sufix: args[0][3] , Rhe valid sufix for the groups if not defined the argument can be an empty string.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        assetName = args[0][1][0]
        prefix = args[0][1][1]
        sufix = args[0][1][2]

        # Get asset grp
        assetGrp = self.assetGroup( assetName = assetName, sufix = sufix )

        grps = self.queryAssetGrpChildren( parentNode = assetGrp )

        # First sting need to be upper case.
        self.checkFistUppercase_fix( nodes = grps )

        # Check sufix "_GRP"
        self.checkGroupSufix_fix( nodes = grps, sufix = sufix)

        # check upper case after "_".
        self.checkUpperCase_fix(  nodes = grps ) 

    def groupName_select( self, *args ):
        """
        Select all groups who do not match with naming conventions.
        
        :param args: Are the defined arguments in the project list.  ( priority, assetName, prefix, sufix ).
        :param assetName: args[0][1] , asset name.
        :param prefix: args[0][2] , The valid prefix for the groups if not defined the argument can be an empty string.
        :param sufix: args[0][3] , Rhe valid sufix for the groups if not defined the argument can be an empty string.
        """

        assetName = args[0][1][0]
        prefix = args[0][1][1]
        sufix = args[0][1][2]

        assetGrp = self.assetGroup( assetName = assetName, sufix = sufix )
        incorrectNames = self.groupsName( parentNode = assetGrp, grpPrefix = prefix, grpSufix = sufix )

        pm.select( incorrectNames )

    def groupsName( self, parentNode = '', grpPrefix = '', grpSufix = '' ):
        """
        Query all groups do not mactch naming coventions.

        :param parentNode: Indicate the paretn group the check heirarchy.
        :param grpPrefix: defined group prefix.
        :param grpSufix: defined group sufix.

        :return: Groups do not match naming conventions.
        :rtype: PyNode[]
        """
        
        # Incorrect naming.
        misnamed = []

        # List all hierarchy.
        noValidShapes = [ 'mesh', 'nurbsSurface' ]

        children = pm.listRelatives( parentNode, ad = True, s = False )
        for c in children:
            if pm.nodeType( c ) in noValidShapes:
                children.remove( c )

        # Query all transform node without shape.
        grp = []

        for n in children:
            if not pm.listRelatives( n, s=True ):
                grp.append( n )

        # First sting need to be upper case.
        noUppercase = self.checkFistUppercase( nodes = grp )

        # Check sufix "_GRP"
        noSufix = self.checkGroupSufix( nodes = grp , sufix = grpSufix)

        # check upper case after "_".
        nextUpper = self.checkUpperCase( nodes = grp ) 

        for nList in [ noUppercase, noSufix, nextUpper ]:
            misnamed.extend( nList )

        return misnamed

    def queryAssetGrpChildren( self, parentNode = '' ):
        """
        Query all children hierarchy transforms.

        :param parentNode: Indicate the paretn group the check heirarchy.

        :return: object list
        :rtype: PyNode[]
        """

        # List all hierarchy.
        grps = []

        for c in pm.listRelatives( parentNode, ad = True, s = False ):

            try:
                if not c.getShape():
                    grps.append( c )
            except:
                pass
                
        return grps

    def checkFistUppercase( self, nodes = [] ):
        """
        Check if the listed nodes starts with uppercase.

        :param nodes: list of nodes to check uppercase:
        
        :return: objects who dont start with uppercase
        :rtype: PyNode[]
        """
        
        # First sting need to be upper case.
        noUppercase = []
        for n in nodes:
            if not n.name()[0].isupper(): 
                noUppercase.append( n )

        return noUppercase

    def checkFistUppercase_fix( self, nodes = [] ):
        """
        This function capitalize objects name.

        :param nodes: list of nodes outside of naming conventions.
        """
        # Query all objects who name is not capitalized.
        filterNodes = self.checkFistUppercase( nodes = nodes )

        # First sting need to be upper case.
        for n in filterNodes:
            if not n.name()[0].isupper(): 

                try:
                    n.rename( n.name().capitalize() )
                except:
                    mc.warning( 'Error {} capitalize'.format( n.name() ) )

    def checkGroupSufix( self, nodes = [], sufix = '_GRP' ):
        """
        Query objects who do not end with the correct sufix.

        :param nodes: PyNode object list to check sufix.
        :param sufix: Defined sufix. ( default "_GRP" )

        :return: objects who do not end with sufix.
        :rtype: PyNode[]
        """
        noSufix = []

        for n in nodes:
            if not n.name().endswith( sufix ):
                noSufix.append( n )

        return noSufix

    def checkGroupSufix_fix( self,  nodes = [] , sufix = '_GRP' ):
        """
        Fix group name adding sufix.
        """

        # Query objects who not end with the correct sufix.
        filterNodes = self.checkGroupSufix( nodes = nodes, sufix = sufix )

        for n in filterNodes:
            if not n.endswith( sufix ):
                try:
                    n.rename( n.name() + sufix )
                except:
                    mc.warning( 'Error {0} in the suffix, could not be fixed'.format( n.name() ) )

    def checkUpperCase( self, nodes = [] ):
        """
        This function check if after every underscore the next string is uppercase.

        :param nodes: list of nodes outside of naming conventions.

        :return: PyNode object list who do not match the name conventions. 
        :rtype: PyNode[]
        """

        noUpperCase = []

        for n in nodes:
            splitName = n.name().split('_')
            for x in splitName:
                if not x[0].isupper():
                    noUpperCase.append( n )
                    break

        return noUpperCase

    def checkUpperCase_fix( self, nodes = []  ):
        """
        This function convert every character after underscore to an uppercase.

        :param nodes: List of nodes outside of naming conventions.
        """

        # Query nodes
        noUpperCase = self.checkUpperCase( nodes = nodes )
        if noUpperCase:

            for n in noUpperCase:
                
                composedName = [] # Store temp name.

                splitName = n.name().split('_') # Split name.
                for x in splitName:
                    if not x[0].isupper():
                        composedName.append( x.capitalize() )
                    else:
                        composedName.append( x )
                
                correctName = '_'.join( composedName ) # Join name.
                # Rename.
                n.rename( correctName )

    def hierarchy_check( self, *args ):
        """
        This function indicates if the hierarchy is correctly ordered. All nodes and groups need to be under the asset name group.

        :param args: Arguments defined in the project list.  ( priority ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """       
        assetName = args[0][1]
  
        priority = args[0][0]

        assemblies = self.assemblyHierarchy( assetName = assetName )

        if assemblies:

            state = 2 # Error state
            note = 'Error, no match shape name : \n' + str( assemblies )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, no match shape name : \n' + str( assemblies )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def hierarchy_fix( self, *args ):
        """
        Query all DAG transforms groups and parent under main asset group.
        """

        assetName = args[0][1]
        # Query main asset group.
        assetGrp = self.assetGroup( assetName = assetName )
        # Query all assemblies DAG nodes.
        assemblies = self.assemblyHierarchy( assetName = assetName )

        # Parent assemblies under main asset group.
        mc.parent( assemblies, assetGrp )

    def hierarchy_select( self, *args ):
        """
        Select all DAG objects outside the main asset group.
        """
        assetName = args[0][1]
        # Query all assemblies DAG nodes. ( global var assetName defined in hierarchy_check method )
        assemblies = self.assemblyHierarchy( assetName = assetName )

        # Select assemblies.
        mc.select ( assemblies )

    def queryTransformsOrientation( self, orientation = None ):
        """
        finds objects that do not match the defined orientation.

        :param orientation: Defined on the project list , ( XYZ = (1,1,1) Yup zFront )
        
        :return: list of objest does not match the orientation.
        :rtype: string[]
        """
        
        # Incorrect orientation nodes. 
        wrongNodes = []
        tNodes = []

        # List all transforms nodes 
        for n in pm.ls( type = 'transform', l = True ):
            if n.getShape():
                if pm.objectType( n.getShape() ) != 'camera':
                    tNodes.append( n.name() )


        for n in tNodes:
            
            # Query transform matrix.
            world_mat = mc.xform( n, q=True, m=True, ws=True)
            # Query axis. 
            x_axis = world_mat[0:3]
            y_axis = world_mat[4:7]
            z_axis = world_mat[8:11]

            if x_axis != [ orientation[0], 0, 0 ]:
                wrongNodes.append( n )
                continue
                
            if y_axis != [ 0, orientation[1], 0 ]:
                wrongNodes.append( n )
                continue
                
            if z_axis != [ 0, 0, orientation[2] ]:
                wrongNodes.append( n )
                continue

        return wrongNodes

    def orientation_check( self, *args ):
        """
        This function indicates if there objects in scene dose not match the defined orientation .

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.
        :param orientation: Defined on the project list , ( XYZ = (1,1,1) Yup zFront )

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        orientation = args[0][1] 

        nodes = self.queryTransformsOrientation( orientation = orientation )
        
        if nodes:
    
            state = 2 # Error state
            note = 'Error, objects axis orientation : \n' + str( nodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, objects axis orientation : \n' + str( nodes )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 
    
    def orientation_select( self, *args ):
        """
        Select objects in scene dose not match the defined orientation .
        """
    
        orientation = args[0][1] 
        nodes = self.queryTransformsOrientation( orientation = orientation )
        mc.select( nodes )

    def getBoundingBox( self ):
        """
        Query bounding box for mesh in scene and idicate if they are under the grid.

        :return: List of objects idicate if the object is under grid.
        :rtype: tupla(bool, obj )[]
        """
        # List all mesh type objects.
        meshList = mc.ls( type = 'mesh' )
        # Query mesh list boundingbox.
        globalBB = mc.exactWorldBoundingBox( meshList )

        objs = []
        for x in meshList:
            bb = mc.exactWorldBoundingBox( x )
            if bb[1] < 0.0:
                objs.append( x )

        # Below.  
        if globalBB[1] < 0.0:
            return ( True, objs )
        else:
            return ( False, None )

    def onAboveOrigin_check( self, *args ):
        """
        This function indicates if there objects under the grid.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        
        priority = args[0][0]
        onAbove = self.getBoundingBox()
        
        if onAbove[0]:
        
            state = 2 # Error state
            note = 'Error, some objects shapes are below origin : \n' + str( onAbove[1] )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects shapes are below origin : \n' + str( onAbove[1] )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def onAboveOrigin_select( self, *args ):
        """
        Select objects who mesh or fraction of the mesh are under the grid.
        """
        onAbove = self.getBoundingBox()
        if onAbove[1]:
            mc.select( onAbove[1] )

    def getAllCams( self ):
        """
        Collect all camera node type in the scene , excluding the default cameras.

        :return: camera in scene.
        :rtype: string[]
        """

        cams = []
        camShape = mc.ls( type = 'camera' )
        defCams = [ 'persp', 'top', 'side', 'front' ]

        # Get camera transform.
        for c in camShape:
            cParent = mc.listRelatives( c, parent = True )[0]
            if cParent not in defCams:
                cams.append( cParent )

        # Get lookAt camera group ( camera aim )
        lookAt = mc.ls( type = 'lookAt' )
        try:
            cams = cams + lookAt
        except:
            pass

        return cams

    def deleteCustomeCameras_check( self, *args ):
        """
        This funciton indicate if there extra cameras in scene.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """


        priority = args[0][0]

        cams = self.getAllCams()

        if cams:
            
            state = 2 # Error state
            note = 'Error, some objects shapes are below origin : \n' + str( cams )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects shapes are below origin : \n' + str( cams )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def deleteCustomeCameras_fix( self, *args ):
        """
        Delete all cameras in scene.
        undo: available.
        """

        cams = self.getAllCams()

        mc.undoInfo( openChunk = True )
        try:
            mc.delete( cams )
        except:
            pass

        try:
            lookAt = mc.ls( type = 'lookAt')
            mc.delete( lookAt )
        except:
            pass

        mc.undoInfo( closeChunk = True )

    def deleteCustomeCameras_select( self, *args ):
        """
        Select all camers in scene.
        """
        cams = self.getAllCams()

        try:
            mc.select( cams )
        except:
            pass

    def noKeyframes_check( self, *args ):
        """
        This function indicate if there keyframes in the scene.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """


        priority = args[0][0]

        # List animCruves* nodes.
        animCurves = mc.ls ( type = 'animCurve' )

        if animCurves:

            state = 2 # Error state
            note = 'Error, objects with keyframe attributes. '

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, objects with keyframe attributes'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def noKeyframes_fix( self, *args ):
        """
        Delete all 'animCurve' nodes.
        :args: none 
        """

        # List animCruves* nodes.
        animCurves = mc.ls ( type = 'animCurve' )

        mc.undoInfo( openChunk = True )

        # Set current time at frame 1,
        mc.currentTime( 1 )

        # Delete keyframes
        try:
            mc.delete( animCurves )
        except:
            pass

        mc.undoInfo( closeChunk = True )

    def noKeyframes_select( self, *args ):
        """
        Select objects with keyframes.
        """

        # List animCruves* nodes.
        animCurves = mc.ls ( type = 'animCurve' )

        objs = []

        if animCurves:
            for x in animCurves:
                print (x)
                if mc.listConnections( x + '.output' )[0]:
                    objs.append( mc.listConnections( x + '.output' )[0] ) 
                    
        objs = set( objs ) 

        mc.select ( objs )

    def noLayers_check( self, *args ):
        """
        Check if exists display layers in scene.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
      
        priority = args[0][0]

        # List all displayLayers.
        dispLay = mc.ls( type = 'displayLayer' )
        # Remove defaultLayer.
        dispLay.remove( 'defaultLayer' )

        if dispLay:
    
            state = 2 # Error state
            note = 'Error, objects with keyframe attributes. '

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, objects with keyframe attributes'

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ False, '' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 


    def noLayers_fix( self, *args ):
        """
        Delete exists display layers in scene.
        """
        
        dispLay = mc.ls( type = 'displayLayer' )
        dispLay.remove( 'defaultLayer' )

        mc.undoInfo( openChunk = True )
        try:
            mc.delete( dispLay )
        except:
            pass
        mc.undoInfo( closeChunk = True )

    def noCurves_check( self, *args ):
        """
        Check if exists nurbsCurve type node in scene.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        nurbsCrv = mc.ls( type = 'nurbsCurve' )

        if nurbsCrv:
        
            state = 2 # Error state
            note = 'Error, there are nurbsCurve in the scene. '

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, there are nurbsCurve in the scene. '

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def noCurves_fix( self, *args ):
        """
        Delete nurbsCurve node type in scene.
        """

        nurbsCrv = mc.ls( type = 'nurbsCurve' )

        mc.undoInfo( openChunk = True )
        try:
            mc.delete( nurbsCrv )
        except:
            pass
        mc.undoInfo( closeChunk = True )

    def noCurves_select( self, *args ):
        """
        Select nurbsCUrve node type.
        """
        nurbsCrv = mc.ls( type = 'nurbsCurve' )
        mc.select( nurbsCrv )
     
    def extensionFile_check( self, *args ):
        """
        Check is the scene are save and extension. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param extension: args[0][1] , Indicates the format that the scene should be.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        extension = args[0][1]

        file = mc.file( sn = True, q = True )

        ext = file.split('.')[-1]

        if not ext == extension:
            
            state = 2 # Error state
            note = 'Error, save file as ".{0}". \n{1}'.format( extension, file )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, save file as ".{0}". \n{1}'.format( extension, file )


            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def unknowNodes_check( self, *args ):
        """
        Check for unknown nodes in scene. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        unknown = mc.ls( type = 'unknown' )

        if unknown:
            
            state = 2 # Error state
            note = 'Error, save file as : \n{0}'.format( unknown )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, save file as : \n{0}'.format( unknown )


            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def unknowNodes_fix( self, *args ):
        """
        This function delete all unknow nodes in scene.
        undo: available. 
        """
        unknown = mc.ls( type = 'unknown' )

        mc.undoInfo( openChunk = True )

        try:
            mc.delete( unknown )
        except:
            mc.warning( 'Following nodes could not be deleted :', unknown )
            pass

        mc.undoInfo( closeChunk = True )

    def unknowNodes_select( self, *args ):
        """
        Select all unknow nodes in scene.
        """        
        unknown = mc.ls( type = 'unknown' )

        mc.undoInfo( openChunk = True )

        try:
            mc.select( unknown )
        except:
            mc.warning( 'Following nodes could not be deleted :', unknown )
            pass

        mc.undoInfo( closeChunk = True )

    def meshNameConvention( self, prefix = '', allowedPrefix = '', sufix = '', allowedSufix = '', tgtPrefix = '' ):
        """
        Check mesh node name conventions . 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param prefix: args[0][1]
        :param allowedPrefix: args[0][2]
        :param sufix: args[0][3]
        :param allowedSufix: args[0][4]
        :param tgtPrefix: args[0][5]


        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        # Prefix 
        noPrefix = self.meshPrefix( prefix = prefix )

        # Upper case convention 
        noUpperCase = self.meshUpperCase()

        # Target prefix 
        noTgtPrefix = self.targetMeshPrefix_fix( tgtPrefix = tgtPrefix )

        # Combine list.
        misnamedNodes = []

        for x in [ noPrefix, noUpperCase, noTgtPrefix ]:
            try:
                misnamedNodes.extend( x )
            except:
                pass

        return misnamedNodes

    def meshName_check( self, *args ):

        priority = args[0][0]
        assetName = args[0][1]
        nConventions = args[0][2]

        prefix        = nConventions[ 'prefix' ]
        allowedPrefix = nConventions[ 'allowedPrefix' ]
        sufix         = nConventions[ 'sufix' ]
        allowedSufix  = nConventions[ 'allowedSufix' ]
        tgtPrefix     = nConventions[ 'tgtPrefix' ]

        misnamedNodes = self.meshNameConvention( prefix = prefix, allowedPrefix = allowedPrefix, sufix = sufix, allowedSufix = allowedSufix, tgtPrefix = tgtPrefix )


        if misnamedNodes:
            
            state = 2 # Error state
            note = 'Error mesh name conventions : \n{0}'.format( misnamedNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning mesh name conventions : \n{0}'.format( misnamedNodes )


            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def meshName_fix( self, *args ):
        
        nConventions = args[0][2]

        prefix        = nConventions[ 'prefix' ]
        allowedPrefix = nConventions[ 'allowedPrefix' ]
        sufix         = nConventions[ 'sufix' ]
        allowedSufix  = nConventions[ 'allowedSufix' ]
        tgtPrefix     = nConventions[ 'tgtPrefix' ]

        print ( prefix, allowedPrefix, sufix, allowedSufix )


        mc.undoInfo( openChunk = True ) 

        # Prefix 
        self.meshPrefix( prefix = prefix, tgtPrefix = tgtPrefix, fix = True )

        # Upper case 
        noUpperCase = self.meshUpperCase()
        self.meshUpperCase_fix( nodes = noUpperCase )

        # Target prefix 
        self.targetMeshPrefix_fix( prefix = prefix, tgtPrefix = tgtPrefix, fix = True )

        mc.undoInfo( closeChunk = True ) 

    def meshPrefix( self, prefix = 'GEO_', allowedPrefix = '', tgtPrefix = '', fix = False ):

        meshNoPrefix = []

        # List all mesh in scene.
        mesh = pm.ls( type = 'mesh' ) 

        for m in mesh:
            p = m.getParent() # Query shape parent. 
            pName = p.name() # Parent name. 

            if pName.startswith( tgtPrefix ):
                    continue

            if not pName.startswith( prefix ):
                meshNoPrefix.append( p )

                if fix:
                    # Fix prefix
                    p.rename( prefix + pName )

        return meshNoPrefix

    def targetMeshPrefix_fix( self, bsGrp = 'Blendshapes_GRP', prefix = 'GEO_', tgtPrefix = 'TGT_', fix = False ):

        noTgtPrefix = []

        if pm.objExists( bsGrp ):

            tgts = pm.listRelatives( bsGrp, ad = True, s = False )

            for t in tgts:
                print ( 'TARGET: ', t )
                tName = t.name()
                if not tName.startswith( tgtPrefix ):
                    noTgtPrefix.append( t )

                    if fix:
                        try:
                            t.rename( tName.replace( prefix, tgtPrefix ) )
                        except:
                            t.rename( tgtPrefix + tName )

        return noTgtPrefix

    def meshUpperCase( self ):
        
        # List all mesh in scene.
        mesh = pm.ls( type = 'mesh' ) 

        nodes = []

        for m in mesh:
            p = m.getParent() # Query shape parent 
            nodes.append( p )

        noUpperCase = []

        for n in nodes:
            splitName = n.name().split('_')
            for x in splitName:
                if not x[0].isupper():
                    noUpperCase.append( n )
                    break

        return noUpperCase

    def meshUpperCase_fix( self, nodes = [] ):

        nodes = self.meshUpperCase()

        if nodes:
            for n in nodes:
                    
                composedName = []

                splitName = n.name().split('_')
                for x in splitName:
                    if not x[0].isupper():
                        fixName = x[ 0 ].upper() + x[ 1: ]
                        composedName.append( fixName)
                    else:
                        composedName.append( x )
                
                correctName = '_'.join( composedName )

                n.rename( correctName )

    def meshName_select( self, *args ):

        nConventions = args[0][2]

        prefix        = nConventions[ 'prefix' ]
        allowedPrefix = nConventions[ 'allowedPrefix' ]
        sufix         = nConventions[ 'sufix' ]
        allowedSufix  = nConventions[ 'allowedSufix' ]
        tgtPrefix     = nConventions[ 'tgtPrefix' ]


        misnamedNodes = self.meshNameConvention( prefix = prefix, allowedPrefix = allowedPrefix, sufix = sufix, allowedSufix = allowedSufix, tgtPrefix = tgtPrefix )

        pm.select( misnamedNodes )
