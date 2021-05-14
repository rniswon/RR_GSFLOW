namespace RRModelingSystem
{
    partial class Simulation
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
            this.buttonImportTS = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // buttonImportTS
            // 
            this.buttonImportTS.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonImportTS.Location = new System.Drawing.Point(213, 427);
            this.buttonImportTS.Name = "buttonImportTS";
            this.buttonImportTS.Size = new System.Drawing.Size(103, 23);
            this.buttonImportTS.TabIndex = 6;
            this.buttonImportTS.Text = "Run Simulation";
            this.buttonImportTS.UseVisualStyleBackColor = true;
            this.buttonImportTS.Click += new System.EventHandler(this.buttonImportTS_Click);
            // 
            // Simulation
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.buttonImportTS);
            this.Name = "Simulation";
            this.Size = new System.Drawing.Size(550, 499);
            this.Load += new System.EventHandler(this.Simulation_Load);
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.Button buttonImportTS;
    }
}
