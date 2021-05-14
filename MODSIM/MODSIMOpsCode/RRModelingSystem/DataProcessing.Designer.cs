namespace RRModelingSystem
{
    partial class DataProcessing
    {
        /// <summary> 
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Component Designer generated code

        /// <summary> 
        /// Required method for Designer support - do not modify 
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.buttonBrowseModsimFile = new System.Windows.Forms.Button();
            this.cbTSTypeID = new System.Windows.Forms.ComboBox();
            this.buttonImportTS = new System.Windows.Forms.Button();
            this.label3 = new System.Windows.Forms.Label();
            this.txtFeatureContains = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.toolStripStatusLabel1 = new System.Windows.Forms.ToolStripStatusLabel();
            this.toolStripProgressBar1 = new System.Windows.Forms.ToolStripProgressBar();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.radioButton2 = new System.Windows.Forms.RadioButton();
            this.radioButtonUseBase = new System.Windows.Forms.RadioButton();
            this.buttonProcessData = new System.Windows.Forms.Button();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.groupBox1.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.tabPage1.SuspendLayout();
            this.tabPage2.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox1.Controls.Add(this.treeView1);
            this.groupBox1.Location = new System.Drawing.Point(6, 41);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(409, 227);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Timeseries Dataset ";
            // 
            // treeView1
            // 
            this.treeView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.treeView1.HideSelection = false;
            this.treeView1.Location = new System.Drawing.Point(3, 16);
            this.treeView1.Name = "treeView1";
            this.treeView1.Size = new System.Drawing.Size(403, 208);
            this.treeView1.TabIndex = 0;
            // 
            // groupBox3
            // 
            this.groupBox3.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox3.Controls.Add(this.buttonBrowseModsimFile);
            this.groupBox3.Controls.Add(this.cbTSTypeID);
            this.groupBox3.Controls.Add(this.buttonImportTS);
            this.groupBox3.Controls.Add(this.label3);
            this.groupBox3.Controls.Add(this.txtFeatureContains);
            this.groupBox3.Controls.Add(this.label2);
            this.groupBox3.Controls.Add(this.textBox1);
            this.groupBox3.Controls.Add(this.label1);
            this.groupBox3.Location = new System.Drawing.Point(3, 9);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(536, 116);
            this.groupBox3.TabIndex = 2;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Output Data Import";
            // 
            // buttonBrowseModsimFile
            // 
            this.buttonBrowseModsimFile.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonBrowseModsimFile.Location = new System.Drawing.Point(498, 13);
            this.buttonBrowseModsimFile.Name = "buttonBrowseModsimFile";
            this.buttonBrowseModsimFile.Size = new System.Drawing.Size(29, 22);
            this.buttonBrowseModsimFile.TabIndex = 8;
            this.buttonBrowseModsimFile.Text = "...";
            this.buttonBrowseModsimFile.UseVisualStyleBackColor = true;
            this.buttonBrowseModsimFile.Click += new System.EventHandler(this.buttonBrowseModsimFile_Click);
            // 
            // cbTSTypeID
            // 
            this.cbTSTypeID.FormattingEnabled = true;
            this.cbTSTypeID.Items.AddRange(new object[] {
            "<<New>>"});
            this.cbTSTypeID.Location = new System.Drawing.Point(107, 66);
            this.cbTSTypeID.Name = "cbTSTypeID";
            this.cbTSTypeID.Size = new System.Drawing.Size(152, 21);
            this.cbTSTypeID.TabIndex = 7;
            // 
            // buttonImportTS
            // 
            this.buttonImportTS.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonImportTS.Location = new System.Drawing.Point(424, 89);
            this.buttonImportTS.Name = "buttonImportTS";
            this.buttonImportTS.Size = new System.Drawing.Size(103, 23);
            this.buttonImportTS.TabIndex = 6;
            this.buttonImportTS.Text = "Import Data";
            this.buttonImportTS.UseVisualStyleBackColor = true;
            this.buttonImportTS.Click += new System.EventHandler(this.buttonImportTS_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(10, 69);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(62, 13);
            this.label3.TabIndex = 4;
            this.label3.Text = "TSTypeID: ";
            // 
            // txtFeatureContains
            // 
            this.txtFeatureContains.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtFeatureContains.Location = new System.Drawing.Point(107, 42);
            this.txtFeatureContains.Name = "txtFeatureContains";
            this.txtFeatureContains.Size = new System.Drawing.Size(420, 20);
            this.txtFeatureContains.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(10, 45);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(93, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "Feature Contains: ";
            // 
            // textBox1
            // 
            this.textBox1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.textBox1.Location = new System.Drawing.Point(107, 17);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(391, 20);
            this.textBox1.TabIndex = 1;
            this.textBox1.Text = "C:\\Users\\anuragsrivastav\\Desktop\\RRGeoMODSIM_v7PRMSOUTPUT.mdb";
            this.textBox1.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(10, 20);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(60, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "File Name: ";
            // 
            // statusStrip1
            // 
            this.statusStrip1.ImageScalingSize = new System.Drawing.Size(20, 20);
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripStatusLabel1,
            this.toolStripProgressBar1});
            this.statusStrip1.Location = new System.Drawing.Point(0, 310);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(550, 22);
            this.statusStrip1.TabIndex = 4;
            this.statusStrip1.Text = "statusStrip1";
            // 
            // toolStripStatusLabel1
            // 
            this.toolStripStatusLabel1.Name = "toolStripStatusLabel1";
            this.toolStripStatusLabel1.Size = new System.Drawing.Size(118, 17);
            this.toolStripStatusLabel1.Text = "toolStripStatusLabel1";
            // 
            // toolStripProgressBar1
            // 
            this.toolStripProgressBar1.Name = "toolStripProgressBar1";
            this.toolStripProgressBar1.Size = new System.Drawing.Size(100, 16);
            // 
            // groupBox2
            // 
            this.groupBox2.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox2.Controls.Add(this.radioButton2);
            this.groupBox2.Controls.Add(this.radioButtonUseBase);
            this.groupBox2.Controls.Add(this.buttonProcessData);
            this.groupBox2.Controls.Add(this.groupBox1);
            this.groupBox2.Cursor = System.Windows.Forms.Cursors.Arrow;
            this.groupBox2.Location = new System.Drawing.Point(6, 6);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(530, 275);
            this.groupBox2.TabIndex = 5;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Time series processing to MODSIM";
            // 
            // radioButton2
            // 
            this.radioButton2.AutoSize = true;
            this.radioButton2.Location = new System.Drawing.Point(166, 19);
            this.radioButton2.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.radioButton2.Name = "radioButton2";
            this.radioButton2.Size = new System.Drawing.Size(155, 17);
            this.radioButton2.TabIndex = 11;
            this.radioButton2.Text = "Create a \"TS\" MODSIM file";
            this.radioButton2.UseVisualStyleBackColor = true;
            // 
            // radioButtonUseBase
            // 
            this.radioButtonUseBase.AutoSize = true;
            this.radioButtonUseBase.Checked = true;
            this.radioButtonUseBase.Location = new System.Drawing.Point(9, 19);
            this.radioButtonUseBase.Margin = new System.Windows.Forms.Padding(2, 2, 2, 2);
            this.radioButtonUseBase.Name = "radioButtonUseBase";
            this.radioButtonUseBase.Size = new System.Drawing.Size(133, 17);
            this.radioButtonUseBase.TabIndex = 10;
            this.radioButtonUseBase.TabStop = true;
            this.radioButtonUseBase.Text = "Use base MODSIM file";
            this.radioButtonUseBase.UseVisualStyleBackColor = true;
            // 
            // buttonProcessData
            // 
            this.buttonProcessData.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonProcessData.Location = new System.Drawing.Point(421, 243);
            this.buttonProcessData.Name = "buttonProcessData";
            this.buttonProcessData.Size = new System.Drawing.Size(103, 23);
            this.buttonProcessData.TabIndex = 7;
            this.buttonProcessData.Text = "Process Data";
            this.buttonProcessData.UseVisualStyleBackColor = true;
            this.buttonProcessData.Click += new System.EventHandler(this.buttonProcessData_Click);
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPage1);
            this.tabControl1.Controls.Add(this.tabPage2);
            this.tabControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabControl1.Location = new System.Drawing.Point(0, 0);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(550, 310);
            this.tabControl1.TabIndex = 6;
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.groupBox3);
            this.tabPage1.Location = new System.Drawing.Point(4, 22);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage1.Size = new System.Drawing.Size(542, 451);
            this.tabPage1.TabIndex = 0;
            this.tabPage1.Text = "Import MODSIM Output";
            this.tabPage1.UseVisualStyleBackColor = true;
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.groupBox2);
            this.tabPage2.Location = new System.Drawing.Point(4, 22);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage2.Size = new System.Drawing.Size(542, 284);
            this.tabPage2.TabIndex = 1;
            this.tabPage2.Text = "Import Time Series";
            this.tabPage2.UseVisualStyleBackColor = true;
            // 
            // DataProcessing
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.statusStrip1);
            this.Name = "DataProcessing";
            this.Size = new System.Drawing.Size(550, 332);
            this.Load += new System.EventHandler(this.Simulation_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.tabControl1.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            this.tabPage2.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.TreeView treeView1;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripStatusLabel toolStripStatusLabel1;
        private System.Windows.Forms.ToolStripProgressBar toolStripProgressBar1;
        private System.Windows.Forms.ComboBox cbTSTypeID;
        private System.Windows.Forms.Button buttonImportTS;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox txtFeatureContains;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.Button buttonProcessData;
        private System.Windows.Forms.Button buttonBrowseModsimFile;
        private System.Windows.Forms.RadioButton radioButton2;
        private System.Windows.Forms.RadioButton radioButtonUseBase;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPage1;
        private System.Windows.Forms.TabPage tabPage2;
    }
}
