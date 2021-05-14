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
using System.Diagnostics;
using System.IO;

namespace RRModelingSystem
{

    public partial class Simulation : UserControl
    {
        private string _OpsDB { get; set; }
        private string _ModsimFile { get; set; }

        public event ProcessMessage messageOut; // event


        public Simulation(string ModsimFile, string opsDB)
        {
            InitializeComponent();

            _ModsimFile = ModsimFile;
            _OpsDB = opsDB;

        }

        private void Simulation_Load(object sender, EventArgs e)
        {
           
        }

            

        private void buttonImportTS_Click(object sender, EventArgs e)
        {
            string modelExecutableWorkspace = Path.GetDirectoryName(Application.ExecutablePath);
            string modelExecutableFile = Path.Combine(modelExecutableWorkspace, "MODSIM_Model.exe");
            modelExecutableFile = "MODSIM_Model.exe";
            if (modelExecutableFile.Contains(" ")) modelExecutableFile = "\"" + modelExecutableFile + "\"";
            string args = "\""+ _ModsimFile + "\" \"" + _OpsDB + "\"";
            string workdir = Path.GetDirectoryName(_ModsimFile);
            if (workdir.Contains(" ")) workdir = "\"" + workdir + "\"";
            RunCommandCom(modelExecutableFile,args,true, modelExecutableWorkspace);
        }

        public void RunCommandCom(string command, string arguments, bool permanent, string workingDir)
        {
            // runs model in the command line
            using (Process p = new Process())
            {
                ProcessStartInfo pi = new ProcessStartInfo();
                pi.Arguments = " " + (permanent ? "/K" : "/C") + " " + command + " " + arguments;
                pi.FileName = "cmd.exe";
                pi.WorkingDirectory = workingDir;
                p.StartInfo = pi;
                //pi.UseShellExecute = true;
                p.Start();

                // when window closes, the thread will continue 
                //p.WaitForExit();
                //p.Close();
            }
        }


    }
}
