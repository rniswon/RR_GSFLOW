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
        public string ProjectDatabase { get; set; }
        public string ModsimFile { get; set; }

        public RRPreferences()
        {
            InitializeComponent();
        }
    }
}
