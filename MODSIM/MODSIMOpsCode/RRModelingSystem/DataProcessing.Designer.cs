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
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.label4 = new System.Windows.Forms.Label();
            this.radioButtonClearTS = new System.Windows.Forms.RadioButton();
            this.radioButtonLoadTS = new System.Windows.Forms.RadioButton();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.buttonBrowseModsimFile = new System.Windows.Forms.Button();
            this.cbTSTypeID = new System.Windows.Forms.ComboBox();
            this.buttonImportTS = new System.Windows.Forms.Button();
            this.label3 = new System.Windows.Forms.Label();
            this.txtFeatureContains = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.radioButton2 = new System.Windows.Forms.RadioButton();
            this.radioButtonUseBase = new System.Windows.Forms.RadioButton();
            this.buttonProcessData = new System.Windows.Forms.Button();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.groupBox3.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.tabPage2.SuspendLayout();
            this.tabPage1.SuspendLayout();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox1.Controls.Add(this.splitContainer1);
            this.groupBox1.Controls.Add(this.radioButtonClearTS);
            this.groupBox1.Controls.Add(this.radioButtonLoadTS);
            this.groupBox1.Location = new System.Drawing.Point(8, 50);
            this.groupBox1.Margin = new System.Windows.Forms.Padding(4);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Padding = new System.Windows.Forms.Padding(4);
            this.groupBox1.Size = new System.Drawing.Size(690, 326);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Timeseries Dataset ";
            // 
            // splitContainer1
            // 
            this.splitContainer1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.splitContainer1.Location = new System.Drawing.Point(7, 22);
            this.splitContainer1.Name = "splitContainer1";
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.treeView1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Panel2.Controls.Add(this.label4);
            this.splitContainer1.Size = new System.Drawing.Size(676, 271);
            this.splitContainer1.SplitterDistance = 187;
            this.splitContainer1.TabIndex = 14;
            // 
            // treeView1
            // 
            this.treeView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.treeView1.HideSelection = false;
            this.treeView1.Location = new System.Drawing.Point(0, 0);
            this.treeView1.Margin = new System.Windows.Forms.Padding(4);
            this.treeView1.Name = "treeView1";
            this.treeView1.Size = new System.Drawing.Size(187, 271);
            this.treeView1.TabIndex = 0;
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 17);
            this.dataGridView1.MultiSelect = false;
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.ReadOnly = true;
            this.dataGridView1.RowHeadersVisible = false;
            this.dataGridView1.RowHeadersWidthSizeMode = System.Windows.Forms.DataGridViewRowHeadersWidthSizeMode.AutoSizeToAllHeaders;
            this.dataGridView1.RowTemplate.Height = 24;
            this.dataGridView1.Size = new System.Drawing.Size(485, 254);
            this.dataGridView1.TabIndex = 0;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Dock = System.Windows.Forms.DockStyle.Top;
            this.label4.Location = new System.Drawing.Point(0, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(278, 17);
            this.label4.TabIndex = 1;
            this.label4.Text = "Features and TSTypes Included in Dataset";
            // 
            // radioButtonClearTS
            // 
            this.radioButtonClearTS.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.radioButtonClearTS.AutoSize = true;
            this.radioButtonClearTS.Location = new System.Drawing.Point(397, 299);
            this.radioButtonClearTS.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.radioButtonClearTS.Name = "radioButtonClearTS";
            this.radioButtonClearTS.Size = new System.Drawing.Size(141, 21);
            this.radioButtonClearTS.TabIndex = 13;
            this.radioButtonClearTS.Text = "Clear Time Series";
            this.radioButtonClearTS.UseVisualStyleBackColor = true;
            // 
            // radioButtonLoadTS
            // 
            this.radioButtonLoadTS.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.radioButtonLoadTS.AutoSize = true;
            this.radioButtonLoadTS.Checked = true;
            this.radioButtonLoadTS.Location = new System.Drawing.Point(544, 299);
            this.radioButtonLoadTS.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.radioButtonLoadTS.Name = "radioButtonLoadTS";
            this.radioButtonLoadTS.Size = new System.Drawing.Size(140, 21);
            this.radioButtonLoadTS.TabIndex = 12;
            this.radioButtonLoadTS.TabStop = true;
            this.radioButtonLoadTS.Text = "Load Time Series";
            this.radioButtonLoadTS.UseVisualStyleBackColor = true;
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
            this.groupBox3.Location = new System.Drawing.Point(4, 11);
            this.groupBox3.Margin = new System.Windows.Forms.Padding(4);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Padding = new System.Windows.Forms.Padding(4);
            this.groupBox3.Size = new System.Drawing.Size(715, 143);
            this.groupBox3.TabIndex = 2;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Output Data Import";
            // 
            // buttonBrowseModsimFile
            // 
            this.buttonBrowseModsimFile.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonBrowseModsimFile.Location = new System.Drawing.Point(664, 16);
            this.buttonBrowseModsimFile.Margin = new System.Windows.Forms.Padding(4);
            this.buttonBrowseModsimFile.Name = "buttonBrowseModsimFile";
            this.buttonBrowseModsimFile.Size = new System.Drawing.Size(39, 27);
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
            this.cbTSTypeID.Location = new System.Drawing.Point(143, 81);
            this.cbTSTypeID.Margin = new System.Windows.Forms.Padding(4);
            this.cbTSTypeID.Name = "cbTSTypeID";
            this.cbTSTypeID.Size = new System.Drawing.Size(201, 24);
            this.cbTSTypeID.TabIndex = 7;
            // 
            // buttonImportTS
            // 
            this.buttonImportTS.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonImportTS.Location = new System.Drawing.Point(565, 110);
            this.buttonImportTS.Margin = new System.Windows.Forms.Padding(4);
            this.buttonImportTS.Name = "buttonImportTS";
            this.buttonImportTS.Size = new System.Drawing.Size(137, 28);
            this.buttonImportTS.TabIndex = 6;
            this.buttonImportTS.Text = "Import Data";
            this.buttonImportTS.UseVisualStyleBackColor = true;
            this.buttonImportTS.Click += new System.EventHandler(this.buttonImportTS_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(13, 85);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(79, 17);
            this.label3.TabIndex = 4;
            this.label3.Text = "TSTypeID: ";
            // 
            // txtFeatureContains
            // 
            this.txtFeatureContains.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtFeatureContains.Location = new System.Drawing.Point(143, 52);
            this.txtFeatureContains.Margin = new System.Windows.Forms.Padding(4);
            this.txtFeatureContains.Name = "txtFeatureContains";
            this.txtFeatureContains.Size = new System.Drawing.Size(559, 22);
            this.txtFeatureContains.TabIndex = 3;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(13, 55);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(124, 17);
            this.label2.TabIndex = 2;
            this.label2.Text = "Feature Contains: ";
            // 
            // textBox1
            // 
            this.textBox1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.textBox1.Location = new System.Drawing.Point(143, 21);
            this.textBox1.Margin = new System.Windows.Forms.Padding(4);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(520, 22);
            this.textBox1.TabIndex = 1;
            this.textBox1.Text = "C:\\Users\\anuragsrivastav\\Desktop\\RRGeoMODSIM_v7PRMSOUTPUT.mdb";
            this.textBox1.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(13, 25);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(79, 17);
            this.label1.TabIndex = 0;
            this.label1.Text = "File Name: ";
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
            this.groupBox2.Location = new System.Drawing.Point(8, 7);
            this.groupBox2.Margin = new System.Windows.Forms.Padding(4);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Padding = new System.Windows.Forms.Padding(4);
            this.groupBox2.Size = new System.Drawing.Size(707, 423);
            this.groupBox2.TabIndex = 5;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Time series processing to MODSIM";
            // 
            // radioButton2
            // 
            this.radioButton2.AutoSize = true;
            this.radioButton2.Location = new System.Drawing.Point(221, 23);
            this.radioButton2.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.radioButton2.Name = "radioButton2";
            this.radioButton2.Size = new System.Drawing.Size(196, 21);
            this.radioButton2.TabIndex = 11;
            this.radioButton2.Text = "Create a \"TS\" MODSIM file";
            this.radioButton2.UseVisualStyleBackColor = true;
            // 
            // radioButtonUseBase
            // 
            this.radioButtonUseBase.AutoSize = true;
            this.radioButtonUseBase.Checked = true;
            this.radioButtonUseBase.Location = new System.Drawing.Point(12, 23);
            this.radioButtonUseBase.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.radioButtonUseBase.Name = "radioButtonUseBase";
            this.radioButtonUseBase.Size = new System.Drawing.Size(170, 21);
            this.radioButtonUseBase.TabIndex = 10;
            this.radioButtonUseBase.TabStop = true;
            this.radioButtonUseBase.Text = "Use base MODSIM file";
            this.radioButtonUseBase.UseVisualStyleBackColor = true;
            // 
            // buttonProcessData
            // 
            this.buttonProcessData.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonProcessData.Location = new System.Drawing.Point(561, 384);
            this.buttonProcessData.Margin = new System.Windows.Forms.Padding(4);
            this.buttonProcessData.Name = "buttonProcessData";
            this.buttonProcessData.Size = new System.Drawing.Size(137, 28);
            this.buttonProcessData.TabIndex = 7;
            this.buttonProcessData.Text = "Process Data";
            this.buttonProcessData.UseVisualStyleBackColor = true;
            this.buttonProcessData.Click += new System.EventHandler(this.buttonProcessData_Click);
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPage2);
            this.tabControl1.Controls.Add(this.tabPage1);
            this.tabControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabControl1.Location = new System.Drawing.Point(0, 0);
            this.tabControl1.Margin = new System.Windows.Forms.Padding(4);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(733, 467);
            this.tabControl1.TabIndex = 6;
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.groupBox2);
            this.tabPage2.Location = new System.Drawing.Point(4, 25);
            this.tabPage2.Margin = new System.Windows.Forms.Padding(4);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Padding = new System.Windows.Forms.Padding(4);
            this.tabPage2.Size = new System.Drawing.Size(725, 438);
            this.tabPage2.TabIndex = 1;
            this.tabPage2.Text = "Import Time Series";
            this.tabPage2.UseVisualStyleBackColor = true;
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.groupBox3);
            this.tabPage1.Location = new System.Drawing.Point(4, 25);
            this.tabPage1.Margin = new System.Windows.Forms.Padding(4);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Padding = new System.Windows.Forms.Padding(4);
            this.tabPage1.Size = new System.Drawing.Size(725, 438);
            this.tabPage1.TabIndex = 0;
            this.tabPage1.Text = "Import MODSIM Output";
            this.tabPage1.UseVisualStyleBackColor = true;
            // 
            // DataProcessing
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.tabControl1);
            this.Margin = new System.Windows.Forms.Padding(4);
            this.Name = "DataProcessing";
            this.Size = new System.Drawing.Size(733, 467);
            this.Load += new System.EventHandler(this.Simulation_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).EndInit();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.tabControl1.ResumeLayout(false);
            this.tabPage2.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.TreeView treeView1;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label1;
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
        private System.Windows.Forms.RadioButton radioButtonClearTS;
        private System.Windows.Forms.RadioButton radioButtonLoadTS;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Label label4;
    }
}
