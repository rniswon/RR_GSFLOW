using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace RRModelingSystem
{
    public partial class RRSurfModelingMain : Form
    {
        private Simulation m_SimUserControl;
        private DataProcessing m_DataProcessing;
        private RRPreferences m_RRPreferences;
        public RRSurfModelingMain()
        {
            InitializeComponent();
            //Initialize user controls
            m_SimUserControl = new Simulation();
            //m_DataProcessing = new DataProcessing();
            m_RRPreferences = new RRPreferences();
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            splitContainer1.Panel2.Controls.Clear();
            switch (treeView1.SelectedNode.Text)
            {
                case "Preferences":
                    splitContainer1.Panel2.Controls.Add(m_RRPreferences);
                    m_RRPreferences.Dock = DockStyle.Fill;
                    break;
                case "Data Processing":
                    if (m_DataProcessing == null || m_RRPreferences.hasChanges)
                    {
                        m_DataProcessing = new DataProcessing(m_RRPreferences.textBoxProjectDB.Text, m_RRPreferences.textBoxMODSIMFile.Text);
                        m_DataProcessing.messageOut += ProcessMessage;
                        ProcessMessage($"Active MODSIM File: {m_RRPreferences.textBoxMODSIMFile.Text}");
                    }
                    //m_DataProcessing.ProjectDB = //@"C:\Users\etrianasanchez\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database.mdb";
                    splitContainer1.Panel2.Controls.Add(m_DataProcessing);
                    m_DataProcessing.Dock = DockStyle.Fill;
                    break;
                case "Simulation":
                    m_SimUserControl.ProjectDB = m_RRPreferences.textBoxProjectDB.Text;//@"C:\Users\etrianasanchez\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database.mdb";

                    //m_SimUserControl.ProjectDB = @"C:\Users\etriana\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database.mdb";
                    //m_SimUserControl.ProjectDB = @"C:\Users\etrianasanchez\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database.mdb";
                    //m_SimUserControl.ProjectDB = @"C:\Users\etrianasanchez\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database PRMS.mdb";
                    //m_SimUserControl.ProjectDB = @"C:\Users\anuragsrivastav\Desktop\RRMS_Database.mdb";

                    splitContainer1.Panel2.Controls.Add(m_SimUserControl);
                    m_SimUserControl.Dock = DockStyle.Fill;
                    break;
                default:
                    break;
            }
        }

        private void ProcessMessage(string msg)
        {
            richTextBoxMsgs.SelectionColor = richTextBoxMsgs.ForeColor;
            if (msg.ToLower().Contains("error"))
                richTextBoxMsgs.SelectionColor = System.Drawing.Color.Red;
            richTextBoxMsgs.AppendText(msg + Environment.NewLine);
            richTextBoxMsgs.SelectionStart = richTextBoxMsgs.Text.Length;
            // scroll it automatically
            richTextBoxMsgs.ScrollToCaret();
            //richTextBoxMsgs.AppendText(String.Format("[{0}] {1} {2}", (includeTime ? DateTime.Now.ToString() : ""), msg, (isnewline ? Environment.NewLine : null)));

        }
    }
}
