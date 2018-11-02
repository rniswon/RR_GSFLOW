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
        public RRSurfModelingMain()
        {
            InitializeComponent();
            //Initialize user controls
            m_SimUserControl = new Simulation();
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            splitContainer1.Panel2.Controls.Clear();
            switch (treeView1.SelectedNode.Text)
            {
                case "Simulation":
                    m_SimUserControl.ProjectDB = @"C:\Users\etrianasanchez\Research Triangle Institute\USGS Russian River MODSIM Model - Documents\Modeling\MODSIM_GSFLOW\RRMS_Database.mdb";
                    //m_SimUserControl.ProjectDB = @"C:\Users\anuragsrivastav\Desktop\RRMS_Database.mdb";

                    splitContainer1.Panel2.Controls.Add(m_SimUserControl);
                    m_SimUserControl.Dock = DockStyle.Fill;
                    break;
                default:
                    break;
            }
        }
    }
}
