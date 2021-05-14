using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace RRModelingSystem
{
    public partial class RRPreferences : UserControl
    {
        public bool hasChanges;
        public string ProjectDatabase { get; set; }
        public string ModsimFile { get; set; }

        public RRPreferences()
        {
            InitializeComponent();
        }

        private void textBoxProjectDB_TextChanged(object sender, EventArgs e)
        {
            hasChanges = true;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "Modsim File (*.xy)|*.xy|All files (*.*)|*.*";
                dlg.RestoreDirectory = true;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    textBoxMODSIMFile.Text = dlg.FileName;
                }
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "Database File (*.sqlite)|*.sqlite|All files (*.*)|*.*";
                dlg.RestoreDirectory = true;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    textBoxProjectDB.Text = dlg.FileName;
                }
            }
        }

        private void textBoxMODSIMFile_TextChanged(object sender, EventArgs e)
        {
            hasChanges = true;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog dlg = new OpenFileDialog())
            {
                dlg.Filter = "SQLite Database File (*.sqlite)|*.sqlite|All files (*.*)|*.*";
                dlg.RestoreDirectory = true;
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    textBoxOpsDB.Text = dlg.FileName;
                }
            }
        }
    }
}
