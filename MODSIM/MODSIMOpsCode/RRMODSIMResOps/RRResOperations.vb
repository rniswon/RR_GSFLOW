Imports Csu.Modsim.ModsimIO
Imports Csu.Modsim.ModsimModel
Imports System
'Imports SurfGWModule


Module RRResOperations
    Private m_Model As Model
    'Execution Flags
    Private PRMS As String = "PRMS_OFF"
    Private Operations As Boolean = True

    Sub Main(ByVal RRCmdArgs() As String)
        Dim FileName As String = RRCmdArgs(0)

        If PRMS = "PRMS_ON" Then
            'm_Model = SurfGWModule.GetModel()
        Else
            m_Model = New Model
        End If
        If Operations Then
            AddHandler m_Model.Init, AddressOf OnInitialize
            AddHandler m_Model.IterBottom, AddressOf OnIterationBottom
            AddHandler m_Model.IterTop, AddressOf OnIterationTop
            AddHandler m_Model.Converged, AddressOf OnIterationConverge
            AddHandler m_Model.End, AddressOf OnFinished
            AddHandler m_Model.OnMessage, AddressOf OnMessage
            AddHandler m_Model.OnModsimError, AddressOf OnMessage
        End If
        If PRMS = "PRMS_ON" Then
            'NOTE: the commanD line arguments for this project have to match the command line arguments expeted in the SurfGWModule
            '       For and unknown reason GSFLOW crashed if there are different arguments in this project. 
            'SurfGWModule.Main(RRCmdArgs)
        Else
            XYFileReader.Read(m_Model, FileName)
            Modsim.RunSolver(m_Model)
        End If
        Console.ReadLine()
    End Sub
    Dim LMendocino As Node
    Dim pillsburyIndex, pillsburyStorage As Link
    'minimum flows
    Dim minNodesCollection As New Collection
    Dim accuracyFactor As Integer
    'West Fork
    Dim westForkFlows, westForkMaxRelease As Link
    Private Sub OnInitialize()
        accuracyFactor = 10 ^ m_Model.accuracy
        LMendocino = m_Model.FindNode("LMendocino")
        pillsburyIndex = m_Model.FindLink("PillsburyIndex")
        pillsburyStorage = m_Model.FindLink("PillsburyStorage")
        'Minimum flows
        Dim m_MinNode As Node
        m_MinNode = m_Model.FindNode("WestJctOps")
        minNodesCollection.Add(m_MinNode, "WestJctOps")
        m_MinNode = m_Model.FindNode("HopelandOps")
        minNodesCollection.Add(m_MinNode, "HopelandOps")
        m_MinNode = m_Model.FindNode("CloverdaleOps")
        minNodesCollection.Add(m_MinNode, "CloverdaleOps")
        m_MinNode = m_Model.FindNode("HealdsburgOps")
        minNodesCollection.Add(m_MinNode, "HealdsburgOps")
        'West Fork Flow
        westForkFlows = m_Model.FindLink("WestForkFlow")
        westForkMaxRelease = m_Model.FindLink("WestForkReleaseMax")
    End Sub

    Private Sub OnIterationTop()
        'Get the condition of the Pillsbury Inflow
        Dim myDate As DateTime = m_Model.TimeStepManager.Index2Date(m_Model.mInfo.CurrentModelTimeStepIndex, TypeIndexes.ModelIndex)
        Dim thisYearCheck As New DateTime(Year(myDate), 5, 31)
        Dim minFlow As Integer
        'Set the state in May 31st for the Case 1 the remaining of the year.
        Dim LMStor As Integer = (LMendocino.mnInfo.start + pillsburyStorage.mlInfo.flow) / accuracyFactor
        If myDate = thisYearCheck Then
            'Evaluates the state in May 31st and stays for the remaining of the year
            If LMStor > 150000 Then
                state = 1
            ElseIf LMStor > 130000 Then
                state = 2
            Else
                state = 3
            End If
        End If
        Select Case pillsburyIndex.mlInfo.flow / accuracyFactor
            Case 1
                If myDate < thisYearCheck Then
                    'Decision before May 31st is independent of the state
                    If myDate < New DateTime(Year(myDate), 4, 1) Then
                        minFlow = 150
                    ElseIf myDate < New DateTime(Year(myDate), 5, 1) Then
                        minFlow = 185
                    Else
                        minFlow = 125
                    End If
                Else
                    If state = 2 Then
                        If myDate >= New DateTime(Year(myDate), 10, 1) And LMStor < 30000 Then
                            state = 4
                        End If
                    End If
                    'Uses the state value set in the May 31st check
                    If state = 1 And myDate >= New DateTime(Year(myDate), 10, 16) Then
                        minFlow = 150
                    ElseIf state = 2 And myDate >= New DateTime(Year(myDate), 10, 16) Then
                        minFlow = 150
                    ElseIf state = 3 And myDate >= New DateTime(Year(myDate), 6, 1) Then
                        minFlow = 75
                    ElseIf state = 4 Then
                        minFlow = 75
                    Else
                        minFlow = 125
                    End If
                End If
            Case 2
                minFlow = 75
            Case 3
                minFlow = 25
        End Select
        'set the minimum flow value in all demands
        'min flow value in CFS - needs to be converted to standard MODSIM english units [acre-ft]
        minFlow = (minFlow + 20) * accuracyFactor * 1.98347 ' Includes the buffer min flow
        For Each node As Node In minNodesCollection
            node.mnInfo.nodedemand(m_Model.mInfo.CurrentModelTimeStepIndex, 0) = minFlow
        Next

        'West Fork flow - Release Check
        If westForkFlows.mlInfo.flow > 2500 * accuracyFactor And m_Model.mInfo.Iteration > 0 Then
            ' 25 cfs in acre-feet per day
            westForkMaxRelease.mlInfo.hi = 49.5867769 * accuracyFactor
        Else
            westForkMaxRelease.mlInfo.hi = 299999999999
        End If
    End Sub

    Private Sub OnMessage(ByVal message As String)
        If PRMS = "PRMS_OFF" Then Console.WriteLine(message)
    End Sub
    Dim state As Integer
    Private Sub OnIterationBottom()

    End Sub

    Private Sub OnIterationConverge()

    End Sub

    Private Sub OnFinished()

    End Sub

End Module
