Imports Csu.Modsim.ModsimIO
Imports Csu.Modsim.ModsimModel
Imports System


Module RRMimimumFlowOperations
    Dim myModel As New Model
    Sub Main(ByVal CmdArgs() As String)
        Dim FileName As String = CmdArgs(0)
        AddHandler myModel.Init, AddressOf OnInitialize
        AddHandler myModel.IterBottom, AddressOf OnIterationBottom
        AddHandler myModel.IterTop, AddressOf OnIterationTop
        AddHandler myModel.Converged, AddressOf OnIterationConverge
        AddHandler myModel.End, AddressOf OnFinished
        AddHandler myModel.OnMessage, AddressOf OnMessage
        AddHandler myModel.OnModsimError, AddressOf OnMessage

        XYFileReader.Read(myModel, FileName)
        Modsim.RunSolver(myModel)
        Console.ReadLine()
    End Sub
    Dim LMendocino As Node
    Dim pillsburyIndex, pillsburyStorage As Link
    'minimum flows
    Dim minNodesCollection As New Collection
    Dim accuracyFactor As Integer
    Private Sub OnInitialize()
        accuracyFactor = 10 ^ myModel.accuracy
        LMendocino = myModel.FindNode("LMendocino")
        pillsburyIndex = myModel.FindLink("PillsburyIndex")
        pillsburyStorage = myModel.FindLink("PillsburyStorage")
        'Minimum flows
        Dim m_MinNode As Node
        m_MinNode = myModel.FindNode("WestJct")
        minNodesCollection.Add(m_MinNode, "WestJct")
        m_MinNode = myModel.FindNode("hopeland")
        minNodesCollection.Add(m_MinNode, "hopeland")
        m_MinNode = myModel.FindNode("Cloverdale")
        minNodesCollection.Add(m_MinNode, "Cloverdale")
        m_MinNode = myModel.FindNode("Healdsburg")
        minNodesCollection.Add(m_MinNode, "Healdsburg")
    End Sub

    Private Sub OnIterationTop()
        'Get the condition of the Pillsbury Inflow
        Dim myDate As DateTime = myModel.TimeStepManager.Index2Date(myModel.mInfo.CurrentModelTimeStepIndex, TypeIndexes.ModelIndex)
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
            node.mnInfo.nodedemand(myModel.mInfo.CurrentModelTimeStepIndex, 0) = minFlow
        Next
    End Sub

    Private Sub OnMessage(ByVal message As String)
        Console.WriteLine(message)
    End Sub
    Dim state As Integer
    Private Sub OnIterationBottom()

    End Sub

    Private Sub OnIterationConverge()

    End Sub

    Private Sub OnFinished()

    End Sub

End Module
