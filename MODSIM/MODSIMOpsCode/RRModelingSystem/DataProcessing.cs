using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Data.OleDb;
using Csu.Modsim.ModsimModel;
using Csu.Modsim.ModsimIO;
using RTI.CWR.MMS_Support;


namespace RRModelingSystem
{
    public delegate void ProcessMessage(string msg);  // delegate
    public partial class DataProcessing : UserControl
    {
        public event ProcessMessage messageOut; // event

        public string ProjectDB { get; set; }
        public string ModsimFile { get; set; }

        public string ProcessModsimFile { get; set; }

        public OleDbConnectionStringBuilder oleConnBuilder = new OleDbConnectionStringBuilder();
        private MyDBSqlite m_DBUtils;

        private Dictionary<string, int> _tsTypeIDs = null;



        public DataProcessing(string dbFile,string MODSIMFile)
        {
            InitializeComponent();

            oleConnBuilder.Provider = "Microsoft.ACE.OLEDB.12.0";
            oleConnBuilder.DataSource = "";

            ProjectDB = dbFile;
            m_DBUtils = new MyDBSqlite(ProjectDB);

            ModsimFile = textBox1.Text;
            ProcessModsimFile = MODSIMFile;
            //Simulation_Load(null,null);
        }

        private void Simulation_Load(object sender, EventArgs e)
        {
            LoadTSTypes();

            LoadScenarios();
        }

        private void buttonBrowseModsimFile_Click(object sender, EventArgs e)
        {
            using(OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "Modsim Ouput (*.mdb)|*.mdb|All files (*.*)|*.*";
                dlg.RestoreDirectory = true;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    textBox1.Text = dlg.FileName;
                }
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            ModsimFile = textBox1.Text;
        }

        private void buttonImportTS_Click(object sender, EventArgs e)
        {
            if (_tsTypeIDs.ContainsKey(cbTSTypeID.Text))
            {
                int tstypeid = _tsTypeIDs[cbTSTypeID.Text];

                // get list of features from the destination database
                DataTable featuredt = GetModsimFeatures(txtFeatureContains.Text.Trim());
                if (featuredt.Rows.Count == 0) return;

                foreach (DataRow r in featuredt.Rows)
                {
                    switch (r["MOD_Type"].ToString())
                    {
                        case "Link":
                            ImportLinkTimeSeries(tstypeid, int.Parse(r["FeatureID"].ToString()), r["MOD_Name"].ToString());
                            break;
                    }
                }
            }
        }

        private void buttonProcessData_Click(object sender, EventArgs e)
        {
            if (treeView1.SelectedNode == null)
            {
                PrintMessage("Error: select a timeseries dataset.");
                return;
            }

            if (!System.IO.File.Exists(ProcessModsimFile))
            {
                PrintMessage("Error: Modsim file does not exists.");
                return;
            }

            ProcessTimeSeriesDataSet();
            PrintMessage("Completed.");
        }
        




        private void LoadTSTypes()
        {
            string cmdtxt = $"SELECT TSTypeID, TSName FROM TSTypes;";
            DataTable dt = m_DBUtils.GetTableFromDB(cmdtxt,"TSType");//ExecuteCommand(cmdtxt);

            // add to colllection
            _tsTypeIDs = new Dictionary<string, int>();            
            foreach (DataRow r in dt.Rows)
            {
                _tsTypeIDs.Add(r["TSName"].ToString(), int.Parse(r["TSTypeID"].ToString()));
                cbTSTypeID.Items.Add(r["TSName"].ToString());
            }

            return;
        }

        private void LoadScenarios()
        {
            string cmdtxt = "SELECT ID, ScnName FROM ScenariosInfo;";
            DataTable dt = m_DBUtils.GetTableFromDB(cmdtxt, "Scns"); //ExecuteCommand(cmdtxt);

            foreach (DataRow r in dt.Rows)
            {
                treeView1.Nodes.Add(r["ID"].ToString(), r["ScnName"].ToString());
            }
        }

        private DataTable GetModsimFeatures(string featurematch)
        {
            string cmdtxt = $"SELECT FeatureID, MOD_Name, MOD_Type FROM Features WHERE MOD_Name LIKE '%{featurematch}%';";
            DataTable dt = m_DBUtils.GetTableFromDB(cmdtxt, "Features"); //ExecuteCommand(cmdtxt);
            return dt;
        }

        private void ImportLinkTimeSeries(int tstypeid, int featureid, string featurename)
        {
            OleDbConnection conn = null;
            try
            {
                string sql =  "INSERT INTO TimeSeries " +
                        $"SELECT T.TSDate AS TSDate, '{featureid}' AS FeatureID, '{tstypeid}' AS TSTypeID, L.Flow AS TSValue FROM " +
                        "(" +
                        $"(SELECT* FROM LinksOutput IN '{ModsimFile}') AS L " +
                        $"INNER JOIN(SELECT* FROM TimeSteps IN '{ModsimFile}') AS T ON T.TSIndex = L.TSIndex " +
                        ") " +
                        $"WHERE L.LNumber = (SELECT LNumber FROM LinksInfo IN '{ModsimFile}' WHERE LName like '{featurename}'); ";
                int result = m_DBUtils.ExecuteQuery(sql);
                PrintMessage($"Feature: {featurename}  - Records affected: {result} in TimeSeries table.");

                //oleConnBuilder.DataSource = ProjectDB;
                //using (conn = new OleDbConnection(oleConnBuilder.ConnectionString))
                //{
                //    conn.Open();

                //    OleDbCommand cmd = conn.CreateCommand();
                //    cmd.CommandText = "INSERT INTO TimeSeries " +
                //        $"SELECT T.TSDate AS TSDate, '{featureid}' AS FeatureID, '{tstypeid}' AS TSTypeID, L.Flow AS TSValue FROM " +
                //        "(" +
                //        $"(SELECT* FROM LinksOutput IN '{ModsimFile}') AS L " +
                //        $"INNER JOIN(SELECT* FROM TimeSteps IN '{ModsimFile}') AS T ON T.TSIndex = L.TSIndex " +
                //        ") " +
                //        $"WHERE L.LNumber = (SELECT LNumber FROM LinksInfo IN '{ModsimFile}' WHERE LName like '{featurename}'); ";

                //    int result = cmd.ExecuteNonQuery();
                //    PrintMessage($"Feature: {featurename}  - Records affected: {result} in TimeSeries table.");
                //}
            }
            catch (Exception ex)
            {
                PrintMessage($"Error: " + ex.Message);
            }
            finally
            {
                if (conn != null && conn.State != ConnectionState.Closed)
                {
                    conn.Close();
                }
            }
        }
        
        private void ProcessTimeSeriesDataSet()
        {
            PrintMessage("Reading MODSIM file ...");

            Model modsim = new Model();
            XYFileReader.Read(modsim, ProcessModsimFile);

            // read the model start date
            DateTime startdate = modsim.TimeStepManager.dataStartDate;
            
            PrintMessage("Getting time-seriesd data ...");

            // get TSTypeIDs
            //string cmdtxt = $"Select TSType From ScenariosTSSet Where Scenario = {treeView1.SelectedNode.Name};";
            //Assume that the units label is the text to set the MODSIM units 
            string cmdtxt = "SELECT ScenariosTSSet.TSType, UnitsInfo.Units, TSTypes.MODSIMTSType" +
                     " FROM UnitsInfo INNER JOIN (ScenariosTSSet INNER JOIN TSTypes ON ScenariosTSSet.TSType = TSTypes.TSTypeID) ON UnitsInfo.UnitsID = TSTypes.UnitsID" +
                    $" WHERE(((ScenariosTSSet.[Scenario]) =  {treeView1.SelectedNode.Name}));";
            DataTable scenariodt = m_DBUtils.GetTableFromDB(cmdtxt, "Scenario");//ExecuteCommand(cmdtxt);

            // for each TSTypeID
            foreach (DataRow sr in scenariodt.Rows)
            {
                cmdtxt = "Select Distinct Timeseries.FeatureID, Features.MOD_Name, Features.MOD_Type, Features.Cost From Timeseries " +
                         $"INNER JOIN  Features on Timeseries.FeatureID = Features.FeatureID where TSTypeID = {sr["TSType"]};";
                DataTable featuresdt = m_DBUtils.GetTableFromDB(cmdtxt, "FeaturesDT");//ExecuteCommand(cmdtxt);
                foreach (DataRow fr in featuresdt.Rows)
                {
                    DataTable tsdt;
                    if (radioButtonLoadTS.Checked)
                    {
                        //cmdtxt = $"Select TSDate AS [Date], ROUND(TSValue * {modsim.ScaleFactor},0) AS HS0 From Timeseries Where FeatureID={fr["FeatureID"]} AND TSTypeID={sr["TSType"]} AND TSDate>='{startdate}' ORDER BY [TSDate];";
                        cmdtxt = "SELECT [Date],max(HS0) AS HS0" +
                                " FROM(" +
                               $"     SELECT TSDate AS [Date], ROUND(TSValue * {modsim.ScaleFactor}, 0) AS HS0" +
                                "     FROM Timeseries" +
                                $"    WHERE FeatureID={fr["FeatureID"]} AND TSTypeID={sr["TSType"]} AND TSDate>='{startdate.ToString("yyyy-MM-dd")}'" +
                                " UNION" +
                                $"    SELECT '{startdate.ToString("yyyy-MM-dd")}', 0" +
                                "   )" +
                                " GROUP BY[Date] ORDER BY[Date]; ";
                        tsdt = m_DBUtils.GetTableFromDB(cmdtxt, "tseries");//ExecuteCommand(cmdtxt);
                    }
                    else
                    {
                        tsdt = new DataTable();
                        tsdt.Columns.Add("Date", typeof(DateTime));
                        tsdt.Columns.Add("HS0", typeof(int));
                        tsdt.Rows.Add(new object[] { startdate.ToString("yyyy-MM-dd"), 0 });
                    }
                    if (tsdt != null)
                    {
                        // apply accuracy factor
                        //tsdt = ApplyAccuracyFactor(tsdt, modsim.accuracy);

                        //check for default units
                        string units = sr["Units"].ToString();
                        if (units == "Dimensionless" || units == "Default") units = "";

                        switch (fr["MOD_Type"].ToString())
                        {
                            case "Link":
                                // assign time-series to MODSIM Link
                                Link link = modsim.FindLink(fr["MOD_Name"].ToString());
                                if (link != null)
                                {
                                    PrintMessage($"Updating time-series for link {link.name}.");
                                    if (sr["MODSIMTSType"].ToString() == "maxVariable")
                                    {
                                        link.m.maxVariable.dataTable = tsdt;
                                        link.m.maxVariable.VariesByYear = true;
                                        link.m.maxVariable.units = units;
                                    }
                                    else if (sr["MODSIMTSType"].ToString() == "adaMeasured")
                                    {
                                        link.m.adaMeasured.dataTable = tsdt;
                                        link.m.adaMeasured.VariesByYear = true;
                                        link.m.adaMeasured.units = units;
                                    }
                                    else
                                        PrintMessage($"  ERROR: MODSIM time series {sr["Units"].ToString()} type not implemented.");
                                    //new ModsimUnits(VolumeUnitsType.kCM, new ModsimTimeStep(ModsimTimeStepType.Monthly)); 

                                    if (fr["Cost"].ToString()!="") 
                                        link.m.cost = long.Parse(fr["Cost"].ToString());// - 150500;
                                }
                                else
                                {
                                    PrintMessage($"link {fr["MOD_Name"]} not found!");
                                }
                                break;
                            case "Demand":
                                // assign time-series to MODSIM Node
                                Node dem = modsim.FindNode(fr["MOD_Name"].ToString());
                                if (dem != null) PopulateTS(dem, dem.m.adaDemandsM, tsdt, units);
                                if (fr["Cost"].ToString() != "" && dem.InflowLinks!=null)
                                {
                                    Link l = dem.InflowLinks.link;
                                    l.m.cost = long.Parse(fr["Cost"].ToString());
                                    PrintMessage($"   Setting demnand inflow link {l.name}.");
                                }
                                break;
                            case "NonStorage":
                                // assign time-series to MODSIM Node
                                Node NSNode = modsim.FindNode(fr["MOD_Name"].ToString());
                                PopulateTS(NSNode, NSNode.m.adaInflowsM, tsdt, units);
                                break;
                            case "Reservoir":
                                // assign time-series to MODSIM Node
                                Node resNode = modsim.FindNode(fr["MOD_Name"].ToString());
                                PopulateTS(resNode, resNode.m.adaTargetsM, tsdt, units);
                                break;
                        }
                    }
                }
            }

            //Generate a File with TS added
            if(!radioButtonUseBase.Checked)
            {
                ProcessModsimFile = ProcessModsimFile.Replace(".xy", "TS.xy");
            }
            PrintMessage($"Writing updated Modsim file...");
            PrintMessage(ProcessModsimFile);

            if (System.IO.File.Exists(ProcessModsimFile))
                if (MessageBox.Show("Output file already exists.  Do you want to overwrite?", "File overwrite", MessageBoxButtons.YesNo)== DialogResult.No)
                {
                    PrintMessage($" --->>> Import ABORTED!");
                    return;
                }
                else
                {
                    System.IO.File.Delete(ProcessModsimFile);
                }
            XYFileWriter.Write(modsim, ProcessModsimFile);
        }

        private void PopulateTS(Node m_Node, TimeSeries m_TimeSeries, DataTable tsdt, string units)
        {
            if (m_Node != null)
            {
                m_TimeSeries.dataTable = tsdt;
                m_TimeSeries.VariesByYear = true;
                if (units != "") m_TimeSeries.units = units;
                //new ModsimUnits(VolumeUnitsType.kCM, new ModsimTimeStep(ModsimTimeStepType.Monthly)); 
                PrintMessage($"Updated time series for node {m_Node.name}");
            }
            else
            {
                PrintMessage($"Node {m_Node.name} not found!");
            }
        }

        private DataTable ApplyAccuracyFactor(DataTable dt, int accuracy)
        {
            foreach (DataRow row in dt.Rows)
            {
                row[1] = Math.Round(double.Parse(row[1].ToString()) * Math.Pow(10, (double)accuracy), 0);
            }
            return dt;
        }

        //private DataTable ExecuteCommand(string commandtext)
        //{
        //    DataTable dt = new DataTable();
        //    OleDbConnection conn = null;

        //    try
        //    {
        //        oleConnBuilder.DataSource = ProjectDB;
        //        using (conn = new OleDbConnection(oleConnBuilder.ConnectionString))
        //        {
        //            conn.Open();
        //            OleDbCommand cmd = conn.CreateCommand();
        //            cmd.CommandText =commandtext;

        //            OleDbDataAdapter adapter = new OleDbDataAdapter(cmd);
        //            adapter.Fill(dt);
        //        }
        //    }
        //    catch (OleDbException ex)
        //    {
        //        PrintMessage($"Error: " + ex.Message);
        //    }
        //    finally
        //    {
        //        if (conn != null && conn.State != ConnectionState.Closed)
        //        {
        //            conn.Close();
        //        }
        //    }

        //    return dt;
        //}

        private void PrintMessage(string msg)
        {
            messageOut.Invoke(msg);
            //richTextBox1.Text += msg + '\n';
            //this.Refresh();
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            LoadFeaturesAndTSTypes();
        }

        private void LoadFeaturesAndTSTypes()
        {
            string cmdtxt = $"SELECT TSTypes.TSTypeID,MOD_Name,MODSIMTSType"+
                            " FROM ScenariosTSSet"+
                            " JOIN TSTypes ON ScenariosTSSet.TSType = TSTypes.TSTypeID"+
                            " JOIN("+
                            "        SELECT Timeseries.FeatureID, TSTypeID, MOD_Name"+
                            "        FROM Timeseries"+
                            "        JOIN Features ON Features.FeatureID = Timeseries.FeatureID"+
                            "        GROUP BY Timeseries.FeatureID"+
                            "    ) as f"+
                            "    ON f.TSTypeID = ScenariosTSSet.TSType"+
                            $" WHERE ScenariosTSSet.Scenario =  {treeView1.SelectedNode.Name}";
            DataTable dt = m_DBUtils.GetTableFromDB(cmdtxt, "FeatTSType");//ExecuteCommand(cmdtxt);

            // add to colllection
            dataGridView1.DataSource = dt;
        }
    }
}
