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


namespace RRModelingSystem
{
    public partial class Simulation : UserControl
    {
        public string ProjectDB { get; set; }
        public string ModsimFile { get; set; }

        public string ProcessModsimFile { get; set; }

        public OleDbConnectionStringBuilder oleConnBuilder = new OleDbConnectionStringBuilder();


        private Dictionary<string, int> _tsTypeIDs = null;



        public Simulation()
        {
            InitializeComponent();

            oleConnBuilder.Provider = "Microsoft.ACE.OLEDB.12.0";
            oleConnBuilder.DataSource = "";

            ModsimFile = textBox1.Text;
            ProcessModsimFile = textBox2.Text;
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

        private void buttonBrowseProcessFile_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "Modsim File (*.xy)|*.xy|All files (*.*)|*.*";
                dlg.RestoreDirectory = true;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    textBox2.Text = dlg.FileName;
                }
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            ModsimFile = textBox1.Text;
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {
            ProcessModsimFile = textBox2.Text;
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
            DataTable dt = ExecuteCommand(cmdtxt);

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
            DataTable dt = ExecuteCommand(cmdtxt);

            foreach(DataRow r in dt.Rows)
            {
                treeView1.Nodes.Add(r["ID"].ToString(), r["ScnName"].ToString());
            }
        }

        private DataTable GetModsimFeatures(string featurematch)
        {
            string cmdtxt = $"SELECT FeatureID, MOD_Name, MOD_Type FROM Features WHERE MOD_Name LIKE '%{featurematch}%';";
            DataTable dt = ExecuteCommand(cmdtxt);
            return dt;
        }

        private void ImportLinkTimeSeries(int tstypeid, int featureid, string featurename)
        {
            OleDbConnection conn = null;
            try
            {
                oleConnBuilder.DataSource = ProjectDB;
                using (conn = new OleDbConnection(oleConnBuilder.ConnectionString))
                {
                    conn.Open();

                    OleDbCommand cmd = conn.CreateCommand();
                    cmd.CommandText = "INSERT INTO TimeSeries " +
                        $"SELECT T.TSDate AS TSDate, '{featureid}' AS FeatureID, '{tstypeid}' AS TSTypeID, L.Flow AS TSValue FROM " +
                        "(" +
                        $"(SELECT* FROM LinksOutput IN '{ModsimFile}') AS L " +
                        $"INNER JOIN(SELECT* FROM TimeSteps IN '{ModsimFile}') AS T ON T.TSIndex = L.TSIndex " +
                        ") " +
                        $"WHERE L.LNumber = (SELECT LNumber FROM LinksInfo IN '{ModsimFile}' WHERE LName like '{featurename}'); ";

                    int result = cmd.ExecuteNonQuery();
                    PrintMessage($"Feature: {featurename}  - Records affected: {result} in TimeSeries table.");
                }
            }
            catch (OleDbException ex)
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
            string cmdtxt = "SELECT ScenariosTSSet.TSType, UnitsInfo.Units" +
                     " FROM UnitsInfo INNER JOIN (ScenariosTSSet INNER JOIN TSTypes ON ScenariosTSSet.TSType = TSTypes.TSTypeID) ON UnitsInfo.UnitsID = TSTypes.UnitsID" +
                    $" WHERE(((ScenariosTSSet.[Scenario]) =  {treeView1.SelectedNode.Name}));";
            DataTable scenariodt = ExecuteCommand(cmdtxt);

            // for each TSTypeID
            foreach(DataRow sr in scenariodt.Rows)
            {
                cmdtxt = "Select Distinct Timeseries.FeatureID, Features.MOD_Name From Timeseries " +
                         $"INNER JOIN  Features on Timeseries.FeatureID = Features.FeatureID where TSTypeID = {sr["TSType"]};";
                DataTable featuresdt = ExecuteCommand(cmdtxt);
                foreach(DataRow fr in featuresdt.Rows)
                {
                    cmdtxt = $"Select TSDate AS [Date], TSValue AS HS0 From Timeseries Where FeatureID={fr["FeatureID"]} AND TSTypeID={sr["TSType"]} AND TSDate>=DateValue('{startdate}') ORDER BY [TSDate];";
                    DataTable tsdt = ExecuteCommand(cmdtxt);

                    if (tsdt != null)
                    {
                        // apply accuracy factor
                        tsdt = ApplyAccuracyFactor(tsdt, modsim.accuracy);

                        // assign time-series to MODSIM file
                        Link link = modsim.FindLink(fr["MOD_Name"].ToString());
                        if (link != null)
                        {
                            link.m.maxVariable.dataTable = tsdt;
                            link.m.maxVariable.VariesByYear = true;
                            link.m.maxVariable.units = (String) sr["units"];
                            //new ModsimUnits(VolumeUnitsType.kCM, new ModsimTimeStep(ModsimTimeStepType.Monthly)); 
                            PrintMessage($"Updated time-series for link {link.name}");
                            link.m.cost = -150500;
                        }
                        else
                        {
                            PrintMessage($"link {fr["MOD_Name"]} not found!");
                        }
                    }
                }
            }

            PrintMessage($"Writing updated Modsim file...");
            XYFileWriter.Write(modsim, ProcessModsimFile);
        }

        private DataTable ApplyAccuracyFactor(DataTable dt, int accuracy)
        {
            foreach (DataRow row in dt.Rows)
            {
                row[1] = Math.Round(double.Parse(row[1].ToString()) * Math.Pow(10, (double)accuracy), 0);
            }
            return dt;
        }

        private DataTable ExecuteCommand(string commandtext)
        {
            DataTable dt = new DataTable();
            OleDbConnection conn = null;

            try
            {
                oleConnBuilder.DataSource = ProjectDB;
                using (conn = new OleDbConnection(oleConnBuilder.ConnectionString))
                {
                    conn.Open();
                    OleDbCommand cmd = conn.CreateCommand();
                    cmd.CommandText =commandtext;

                    OleDbDataAdapter adapter = new OleDbDataAdapter(cmd);
                    adapter.Fill(dt);
                }
            }
            catch (OleDbException ex)
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

            return dt;
        }

        private void PrintMessage(string msg)
        {
            richTextBox1.Text += msg + '\n';
            this.Refresh();
        }


    }
}
