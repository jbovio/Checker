
import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm


class Lookdev():

    def listDeformers( self, nType = None ):
        """
        Lists all requested deformers.

        :param args: ( *, [ priority, deformers type ] )
        :return: List of deformers names in scene.
        :rtype: string[]
        """

        # List all defrormers by type.
        deformersNodes = []

        for defType in nType:
            deformersNodes.extend(  mc.ls( type = defType ) ) 

        return deformersNodes

    def clearDeformers_check( self, *args ):
        """
        Check for type of deformers exist in scene. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param deformerType: args[0][1] , Type of deformers to check for.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        deformerType = args[0][1]
        deformerNodes = self.listDeformers( deformerType )

        if deformerNodes:
    
            state = 2 # Error state
            note = 'Error, some objects have active deformeres. Deformers: ( {0} ) \n ( {1} )'.format( deformerType, deformerNodes )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, some objects have active deformeres. Deformers: ( {0} ) \n ( {1} )'.format( deformerType, deformerNodes )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def clearDeformers_fix( self, *args ):
        """
        Turn off deformer envelope and delete it.
        """

        deformerType = args[0][1]
        dNodes = self.listDeformers( deformerType )

        errorNodes = []

        mc.undoInfo( openChunk = True )

        for n in dNodes:
            try:
                mc.setAttr( n + '.envelope', 0 ) # Set envelop 
                mc.delete( n )
            except:
                errorNodes.append( n )

        mc.undoInfo( closeChunk = True )

        if errorNodes:
            mc.warning( 'The following nodes could not be reset or deleted, (they may be locked): {0}'.format(errorNodes) )

    def clearDeformers_select( self, *args ):
        """
        Select objects with defined deformers.
        """

        deformerType = args[0][1] 
        dNodes = self.listDeformers( nType = deformerType )
        mc.select( dNodes )

    def delNonDeformHistory_check( self, *args ):
        """
        Bake all "NonDefHistory". 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        # Delte all non-deformer history.
        mm.eval('BakeAllNonDefHistory')
        note = 'All non-deformer history has been deleted.'
        result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def flagGeoWithTransform( self, *args ):
        """
        List all objects if the object have transform flagged with "orange" color in outliner.

        :return: list of objects with transfroms.
        :rtype: string[]
        """

        # List all transform nodes.
        tNodes = mc.ls( type = 'transform' )
        # List cameras.
        cams = mc.ls( type = 'camera' )
        # Remove cameras form tNode list.
        for c in cams:
            cParent = mc.listRelatives( c, p = True )[0]
            print ( cParent ) 
            if cParent in tNodes:
                tNodes.remove(cParent)
                
        # List nodes with transfroms.
        traObjs = []
        for n in tNodes:
            # Query node transforms.
            t = mc.getAttr( n + '.t' )[0]
            r = mc.getAttr( n + '.r' )[0]
            s = mc.getAttr( n + '.scale')[0]
            
            if t != (0.0, 0.0 , 0.0) or r != (0.0, 0.0, 0.0) or s != (1, 1, 1):
                traObjs.append( n )
                # Set outliner color.
                mc.setAttr( n + '.useOutlinerColor', 1 )
                mc.setAttr( n + '.outlinerColor', 1, 0.5, 0 )
            else:
                mc.setAttr( n + '.useOutlinerColor', 0 ) # Set outliner color Off.

        return traObjs

    def flagGeoWithTransform_check( self, *args ):
        """
        Flag DAG objects who have transforms.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        traObjs = self.flagGeoWithTransform()

        if traObjs:
    
            state = 2 # Error state
            note = 'Error, The following objects have transform information: ( {0} ) '.format( traObjs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, The following objects have transform information: ( {0} ) \n '.format( traObjs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def flagGeoWithTransform_select( self, *args ):
        """
        Select objects with transforms.
        """
        traObjs = self.flagGeoWithTransform()
        mc.select( traObjs )

    def flagObjWithDeformHistory( self, *args ):
        """
        Flag objects with deform history.

        :return: List of objects who have history.
        :rtype: string[]
        """
        objWithHis = []

        hobj = mc.ls( type = 'transform' ) 

        for x in hobj:
            his = mc.listHistory(x, pdo = True)
            if his:
                objWithHis.append( x )        
                # Set outliner color. 
                mc.setAttr( x + '.useOutlinerColor', 1 )
                mc.setAttr( x + '.outlinerColor', 1, 0.5, 0 )

            else:

                mc.setAttr( x + '.useOutlinerColor', 0 ) # Set outliner color Off.

                t = mc.getAttr( x + '.t' )[0]
                r = mc.getAttr( x + '.r' )[0]
                s = mc.getAttr( x + '.scale')[0]
            
                if t != (0.0, 0.0 , 0.0) or r != (0.0, 0.0, 0.0) or s != (1, 1, 1):
                    # Set outliner color.
                    mc.setAttr( x + '.useOutlinerColor', 1 )
                    mc.setAttr( x + '.outlinerColor', 1, 0.5, 0 )
                else:
                    mc.setAttr( x + '.useOutlinerColor', 0 ) # Set outliner color Off.



        return objWithHis

    def flagObjWithDeformHistory_check( self, *args ):
        """
        Check for objects who have history. 

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        objs = self.flagObjWithDeformHistory()


        if objs:
    
            state = 2 # Error state
            note = 'Error, The following objects have deform history: ( {0} ) '.format( objs )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, The following objects have deform history: ( {0} ) '.format( objs )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def flagObjWithDeformHistory_select( self, *args ):
        """
        Select objects whit deform history.
        """
        objs = self.flagObjWithDeformHistory()
        mc.select ( objs )
        
    def uvSetName( self, *args ):
        """
        Identify objects with more the one uv sets and incorrect named uv set 
        :return: list of objects with more then one uv set and incorrect named default uv set.
        :rtype: [ string[], string[] ]
        """
        # List all exists mesh in scene.
        mesh = mc.ls( type = 'mesh' )

        moreThenOne = [] # objs with more then one uv set.
        worngName = [] # objs with the incorrectly named uv set.

        for m in mesh:

            UVs = mc.polyUVSet(m, allUVSets = True, q = True )
            if len(UVs) > 1:
                moreThenOne.append( m )
                
            if mc.polyUVSet(m, allUVSets = True, q = True )[0] != 'map1':
                worngName.append( m )

        return [ moreThenOne, worngName ]

    def uvSetName_check( self, *args ):
        """
        Check objects uv sets.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        uvs = self.uvSetName()


        if uvs[1]:
    
            state = 2 # Error state
            note = 'Error, uv set is not named correctly: ( {0} ) '.format( uvs[1] )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, uv set is not named correctly: ( {0} ) '.format( uvs[1] )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def uvSetName_fix( self, *args ):
        """
        Rename default uv set.
        """
        meshList = self.uvSetName()

        for m in meshList[1]:
            try:
                currentUV = mc.polyUVSet( m, allUVSets = True, q = True )[0] # Query UV name at index 0
                mc.polyUVSet( m, newUVSet = 'map1',  uvSet = currentUV, rename = True )
            except:
                mc.warning( 'Failed to change the name in : ', m )

    def uvSetName_select( self, *args ):
        """
        Select objects with incorrect default uv set name. 
        """
        uvs = self.uvSetName()
        mc.select( uvs[1] )

    def multipleUVSet_check( self, *args ):
        """
        Check for objects with multiple uv sets.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        priority = args[0][0]

        uvs = self.uvSetName()


        if uvs[0]:
    
            state = 2 # Error state
            note = 'Error, uv set is not named correctly: ( {0} ) '.format( uvs[1] )

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, uv set is not named correctly: ( {0} ) '.format( uvs[1] )

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def multipleUVSet_select( self, *args ):
        """
        Select objecst with multiple uv sets.
        """
        meshList = self.uvSetName()
        nList = []
        for n in meshList[0]:
            p = mc.listRelatives( n , p = True )[0]
            nList.append( p )
        mc.select( nList )


    def listMaterials( self, prefix = '' ):
        """
        List materials in scene without the correct prefix.

        :param prefix: str 

        :return: list of meterials in scene
        :rtype: string[]
        """
        # List all mats in scene
        mats = mc.ls( mat = True )

        # Remove lambert1 ( default mat)
        try:
            mats.remove( 'lambert1' )
            mats.remove( 'standardSurface1' )
            mats.remove( 'particleCloud1' )
        except:
            pass

        # List of material without the prefix.
        matPrefix = []
        
        for m in mats:
            if m[0: len(prefix) ] != prefix :
                matPrefix.append(m)

        return matPrefix

    def materialPrefix_check( self, *args ):
        """
        Check for materials withou the correct name prefix.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param prefix: args[0][1]

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]
        prefix = args[0][1]
        
        mats = self.listMaterials( prefix )

        if mats:
        
            state = 2 # Error state
            note = 'Error, Materials without the correct prefix: ( {0} ) '.format( mats)

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, Materials without the correct prefix: ( {0} ) '.format( mats )

            result = {'state': state, 'note': note, 'fixBtn': True, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def materialPrefix_fix( self, *args ):
        """
        Rename materials nodes and add prefix.
        undo: available.

        :param prefix: args[0][1] str
        """

        prefix = args[0][1]
        mats = self.listMaterials( prefix )

        mc.undoInfo( openChunk = True )

        for m in mats:
            try:
                mc.rename( m , prefix + m )
            except:
                pass

        mc.undoInfo( closeChunk = True )


    def materialPrefix_select( self, *args ):
        """
        Select materials without the correct prefix.
        :param prefix: args[0][1] 
        """
        prefix = args[0][1]
        mats = self.listMaterials( prefix )
        mc.select( mats )
        
    def defaultMaterialType( self, matType = '' ):
        """
        This function collect all the materials and filter by type.

        :param matType: Defined default material.
        :return: Materials who no are the default type.
        :rtype: string[]
        """

        # List all mats in scene
        mats = mc.ls( mat = True )

        # Remove lambert1 ( default mat)
        try:
            mats.remove( 'lambert1' )
            mats.remove( 'standardSurface1' )
            mats.remove( 'particleCloud1' )
        except:
            pass

        # List diferent materials .
        noTypeMats = []
        for m in mats:
            if mc.nodeType( m ) != matType:
                noTypeMats.append( m )
        
        return noTypeMats

    def defaultMaterialType_check( self, *args ):
        """
        Check for the default type material in scene.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.
        :param matType: args[0][1], material default type.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        priority = args[0][0]
        matType = args[0][1]
        
        mats = self.defaultMaterialType( matType )

        if mats:
        
            state = 2 # Error state
            note = 'Error, the following materials are not {0}: ( {1} ) '.format( matType, mats)

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, the following materials are not {0}: ( {1} ) '.format( matType, mats)

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 
        
    def defaultMaterialType_select( self, *args ):
        """
        Select materials who does not match the default type.
        """
        matType = args[0][1]
        mats = self.defaultMaterialType( matType )
        mc.select( mats )

    def deleteUnusedNode_check( self, *args ):
        """
        Check if there unused nodes in scene, and delete unused nodes.
        undo: available.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """
        mc.undoInfo( openChunk = True )

        mm.eval( 'hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");' ) 

        mc.undoInfo( closeChunk = True )

        note = 'Ok. Delete no use shaders.'
        result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result

    def facesWithoutSG( self, *args ):
        """
        This function looks for face component who don't have a shading group assigned.

        :return: component faces 
        :rtype: string[]
        """

        noShadingGrpFaces = {}

        # List all mesh nodes in scene,
        mesh = mc.ls( type='mesh' ) 

        for m in mesh: # For each mesh 
            
            sgs = mc.listConnections( m , type = 'shadingEngine' ) # List shading groups.
            sgs = set(sgs) 
            allFaces = mc.ls( m + '.f[*]', fl=True) # Query all faces id form the mesh.

            facesWithSG = []

            for sg in sgs: # For shading group.
                faces = []
                members = mc.sets(sg, q = True )
                mc.select( members )
                members = mc.ls( sl=True, fl=True)
                facesWithSG.extend( members )
                
            for f in allFaces:
                if f not in facesWithSG:
                    faces.append( f )

            if faces:
                    meshParent = mc.listRelatives( m , p = True )[0]
                    noShadingGrpFaces[ meshParent ] = faces
                            
        mc.select( cl = True )

        return noShadingGrpFaces
        
    def faceWithoutMaterial( self, *args ):
        """
        This function looks for face component who don't have a material assigned.

        :return: component faces 
        :rtype: string[]
        """

        matDir = {} # Key = object with initialShadiningGroup , value = faces with initialShadiningGroup.
    
        # List all mesh object type in scene.
        sceneMesh = mc.ls( type = 'mesh' )

        for mesh in sceneMesh:
            meshObj = mc.listRelatives( mesh, p = True )[ 0 ] # Get transform.

            refFaces = mc.select( meshObj + '.f[*]' ) # Select faces

            tokenId = mc.ls( sl = 1 )[ 0 ].split( "[" )[ 0 ]  # remember a token for comparison below

            # Query exists materiasl in selected faces
            theNodes = mc.ls( mesh, dag = True, s = True )
            shadeEng = mc.listConnections( theNodes, type = 'shadingEngine' ) # List connectiones 
            materials = mc.ls( mc.listConnections( shadeEng ), type = ( 'lambert' ), materials = True ) # List materials groups

            matList = set( materials ) # Set material list

            for mat in matList:
                # Query shader engine
                sg = mc.listConnections( mat, s = 0, d = 1 )
                
                # Remvoe initialParticleSE
                try:
                    sg.remove( 'initialParticleSE' )
                except:
                    pass

                # Loocking for shading engine node. 
                for s in sg:
                    if s != 'initialShadingGroup':
                        continue 
                        
                    shadingEngine = s                     
                    # 
                    if shadingEngine:
                        faces = []
                        if  mc.sets(shadingEngine, q=1):
                            for o in mc.sets(shadingEngine, q=1):
                                if '.f[' in o:
                                    if tokenId not in o: continue
                                    faces.append(o)
                                    
                            matDir[ meshObj ] = faces 

            mc.select( cl = True )    

        return matDir

    def faceWithoutMaterial_check( self, *args ):
        """
        Check if there component face without material or shading group assigned.
        undo: available.

        :param args: Arguments defined in the project list.  ( priority, orientation ).
        :param priority: args[0][0] , Indicate if the check must be critical or warning.

        :return: dic{ state: int, note: str, fixBtn: bool, extraBtn: [ bool, stg ] }
        :rtype: Dictionary. 
        """

        priority = args[0][0]

        noShaderFaces = self.faceWithoutMaterial()
        noShadingGrpFaces = self.facesWithoutSG()

        faces = {}
        if noShaderFaces:
            faces.update( noShaderFaces )
        
        if noShadingGrpFaces:
            faces.update( noShadingGrpFaces )

        if faces:
            
            state = 2 # Error state
            note = 'Error, Face components with initial shading group assigned or no shader assigned.'

            if priority == 2:
                state = 3 # Warning state.
                note = 'Warning, Face components with initial shading group assigned or no shader assigned.'

            result = {'state': state, 'note': note, 'fixBtn': False, 'extraBtn': [ True, 'Sel' ] }

        else:
            note  = 'Ok.'
            result = {'state': 1, 'note': note, 'fixBtn': False, 'extraBtn': [ False, '' ] }

        return result 

    def faceWithoutMaterial_select( self, *args ):
        """
        Select faces without assigned material.
        """
        noShaderFaces = self.faceWithoutMaterial()
        noShadingGrpFaces = self.facesWithoutSG()

        faces = {}
        if noShaderFaces:
            faces.update( noShaderFaces )
        
        if noShadingGrpFaces:
            faces.update( noShadingGrpFaces )

        mc.select( cl = True )

        for k in faces.keys():
            mc.select( faces[ k ], add = True )

        initialSG = mc.sets('initialShadingGroup', q=True)
        mc.select( initialSG, add = True )

        # Select elements 
        initialSG = mc.sets('initialParticleSE', q=True)
        mc.select( initialSG, add = True )

        filterFaces = mc.filterExpand( selectionMask = 34 )  
        mc.select( filterFaces )

    def disconnectInitialSG( self, *args ):
        """
        Disconect initial shading group from mesh in scene.
        """

        # List all initialSG connections with mesh nodes.
        meshConnected = mc.listConnections('initialShadingGroup', type='mesh', p=True, c=True)

        meshIndex = 1
        sgIndex = 0

        for x in range(0, len( meshConnected ), 2 ):
            try:
                mc.disconnectAttr( meshConnected[ meshIndex ], meshConnected[ sgIndex ] )
            except:
                pass
            
            meshIndex = meshIndex + 1
            sgIndex = sgIndex + 1

