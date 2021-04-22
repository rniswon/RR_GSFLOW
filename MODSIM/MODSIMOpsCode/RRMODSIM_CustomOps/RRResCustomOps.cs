using System;
using System.Collections.Generic;
using System.Text;

using Csu.Modsim.ModsimIO;
using Csu.Modsim.ModsimModel;

using System.IO;
using System.Data;

using RTI.CWR.MMS_Support;

namespace RTI.CWR.RRModel
{
    class Program
    {
        public static Model m_Model = new Model();
        private static string fileName;

        private static Dictionary<string, double[]> modelFactors;
        private static string dataDBPath;

        static void Main(string[] args)
        {

            m_Model.Init += OnInitialize;
            m_Model.IterBottom += OnIterationBottom;
            m_Model.IterTop += OnIterationTop;
            m_Model.Converged += OnIterationConverge;
            m_Model.End += OnFinished;
            m_Model.OnMessage += OnMessage;
            m_Model.OnModsimError += OnError;

            fileName = args[0];
            dataDBPath = args[1];
            XYFileReader.Read(m_Model, fileName);

            int run = Modsim.RunSolver(m_Model);

            if (run == 0)
            {
                Console.WriteLine("Finished MODSIM run!");
            }
                    
            Console.ReadKey();
        }
        
        private static int AccuracyConversion(long value)
        {
            int newValue = (int)(value/m_Model.ScaleFactor);
            return newValue;
        }

        private static Node LMendocino;
        private static Link pillsburyIndex;
        private static Link pillsburyStorage;
        private static Link westForkFlows;
        private static Link MendoContrlledRelease;
        private static Link hopelandGage;
        private static MinFlowCalculator LMendoMinFlow;
        private static int storageState=0;
        private static ReleaseCapacity LMendoRelease;

        private static void OnInitialize()
        {
            InitilizeVariables();
            //min release clases
            LMendoMinFlow = new MinFlowCalculator(dataDBPath, "Mendo_MinFlow_1610QTUCP", ref m_Model);
            LMendocino = m_Model.FindNode("LMendocino");
            pillsburyIndex = m_Model.FindLink("PillsburyIndex");
            pillsburyStorage = m_Model.FindLink("PillsburyStorage");

            //Mendocino Releases (controlled and uncontrolled)
            LMendoRelease = new ReleaseCapacity(dataDBPath, "MendocinoReleases", ref m_Model);


            //West Fork Flow
            westForkFlows = m_Model.FindLink("WestForkFlow");
            MendoContrlledRelease = m_Model.FindLink("Mendo_ControlledRelease");
            hopelandGage = m_Model.FindLink("Hopland_Gage");
        }

        private static void InitilizeVariables()
        {
            modelFactors = new Dictionary<string, double[]>();
            //Monthly Loss factors
            double[] lossFact = new double[12];
            lossFact[0] = 0.1;
            lossFact[1] = 0.2;
            lossFact[2] = 0.3;
            lossFact[3] = 0.4;
            lossFact[4] = 0.5;
            lossFact[5] = 0.6;
            lossFact[6] = 0.7;
            lossFact[7] = 0.8;
            lossFact[8] = 0.8;
            lossFact[9] = 0.8;
            lossFact[10] = 0.8;
            lossFact[11] = 0.8;
            // The dictionary kwy corresponds to the link name in the MODSIM Network
            modelFactors.Add("CLoss_Link", lossFact);
        }

        private static void OnIterationTop()
        {

            if (m_Model.mInfo.Iteration == 0)
            {
                DateTime thisDate = m_Model.TimeStepManager.Index2Date(m_Model.mInfo.CurrentModelTimeStepIndex, TypeIndexes.ModelIndex);
                
                //foreach (string key in modelFactors.Keys)
                //{
                //    Link l = m_Model.FindLink(key);
                //    if(l!=null)l.m.loss_coef = modelFactors[key][mon - 1];
                //}

                //Set operation flows -
                storageState = LMendoMinFlow.GetStorageState(m_Model, LMendocino.mnInfo.start, pillsburyStorage.mlInfo.flow);


                int YearTypeFlag = (int)(pillsburyIndex.mlInfo.flow / m_Model.ScaleFactor);
                if (YearTypeFlag == 1 || YearTypeFlag == 4)
                {
                    LMendoMinFlow.AssignMinFlowsToNodes(m_Model.mInfo.CurrentModelTimeStepIndex, thisDate, storageState.ToString());
                }
                else if (YearTypeFlag == 2 || YearTypeFlag == 3)
                    // YearTypeFlag: 2 & 3
                    // Min flow table uses columns 2 and 3 to store the values per node.
                    LMendoMinFlow.AssignMinFlowsToNodes(m_Model.mInfo.CurrentModelTimeStepIndex, YearTypeFlag.ToString());
                else
                    LMendoMinFlow.AssignMinFlowsToNodes(m_Model.mInfo.CurrentModelTimeStepIndex, thisDate, "1");

            }

            if (m_Model.mInfo.Iteration > 1)
            {
                //Mendocino Releases (Controlled and Uncontrolled)
                LMendoRelease.SetReleaseCapacity(m_Model.mInfo.CurrentModelTimeStepIndex, LMendocino, interpolate: true);

                //West Fork flow - Release Check and overwrite Mendo controlled releases
                if ((westForkFlows != null))
                {
                    //reservoir releases cannot exceed 25 cfs if flow in west fork are > 2500 cfs and flows at Hopland are > 8000 cfs
                    double maxFlow_cfs = 2500 * 1.98347;
                    //If (westForkFlows.mlInfo.flow > maxFlow_cfs * accuracyFactor And hopelandGage.mlInfo.flow > 8000 * 1.98347 * accuracyFactor) And m_Model.mInfo.Iteration > 0 Then
                    if ((westForkFlows.mlInfo.flow > maxFlow_cfs * m_Model.ScaleFactor) && (m_Model.mInfo.Iteration > 0))
                    {
                        // 25 cfs in acre-feet per day
                        if (MendoContrlledRelease != null)
                            //MendoContrlledRelease.mlInfo.hi = (long)Math.Round((49.5867769 * m_Model.ScaleFactor), 0);
                            MendoContrlledRelease.mlInfo.hiVariable[m_Model.mInfo.CurrentModelTimeStepIndex, 0] = (long)Math.Round((49.5867769 * m_Model.ScaleFactor), 0);
                    }
                }
            }
        }

        private static void OnMessage(string message)
        {
            Console.WriteLine(message);
        }

        private static void OnError(string message)
        {
            Console.WriteLine(message);
        }

        private static void OnIterationBottom()
        {
            //long a = MendoContrlledRelease.mlInfo.hi;
            //MendoContrlledRelease.mlInfo.hi = MendoContrlledRelease.mlInfo.hiVariable[m_Model.mInfo.CurrentModelTimeStepIndex, 0];
        }

        private static void OnIterationConverge()
        {
        }

        private static void OnFinished()
        {
        }
    }
}
