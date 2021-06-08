using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace cyto_control
{
    class main_program
    {
        public static class GlobalFlag
        {
            public static bool isActionComplete = false;
            public static bool isServerReady = false;
            public static bool isInstrumentStandBy = false;
        }

        public static void OnActionCompleted(object sender, CytExpertAPI.API.ActionCompletedEventArgs e)
        {
            Console.WriteLine("Action Completed: {0}", e.Message.MessageType);
            GlobalFlag.isActionComplete = e.Message.ActionSuccess;
            Console.WriteLine(e.Message.ActionSuccess);
        }
        public static void OnStateUpdated(object sender, CytExpertAPI.API.StateUpdatedEventArgs e)
        {
            // Console.WriteLine(e.Message);
            switch (e.Message.MessageType)
            {
                case CytExpertAPI.Messages.EMessageType.ServerState:
                    // Console.WriteLine("Updated Server State");
                    CytExpertAPI.Messages.ServerStateMessage _serverStateMessage = (CytExpertAPI.Messages.ServerStateMessage)e.Message;
                    // Console.WriteLine(_serverStateMessage.ServerState);
                    if (_serverStateMessage.ServerState == CytExpertAPI.Messages.EServerState.Ready)
                    {
                        GlobalFlag.isServerReady = true;
                    }
                    break;
                case CytExpertAPI.Messages.EMessageType.InstrumentState:
                    // Console.WriteLine("Updated Instrument State");
                    CytExpertAPI.Messages.InstrumentStateMessage _instrumentStateMessage = (CytExpertAPI.Messages.InstrumentStateMessage)e.Message;
                    // Console.WriteLine(_instrumentStateMessage.InstrumentState);
                    if (_instrumentStateMessage.InstrumentState == CytExpertAPI.Messages.EInstrumentWorkState.Standby)
                    {
                        GlobalFlag.isInstrumentStandBy = true;
                    }
                    break;
            }

        }
        public static void OnTubeRecordResultGenerated(object sender, CytExpertAPI.API.TubeRecordResultGeneratedEventArgs e)
        {
            Console.WriteLine("On Tube Record Result Generated");
        }

        static void Main(string[] args)
        {
            Console.WriteLine("ALL SYSTEMS NORMINAL");
            CytExpertAPI.API.ICytExpertAutomation _cytExpertAutomation = CytExpertAPI.API.CytExpertAutomationFactory.GetInstance();
            CytExpertAPI.API.ICytExpertAutomationEvent _cytExpertAutomationEvent = _cytExpertAutomation as CytExpertAPI.API.ICytExpertAutomationEvent;
            if (_cytExpertAutomationEvent != null)
            {
                _cytExpertAutomationEvent.ActionCompleted += OnActionCompleted;
                _cytExpertAutomationEvent.StateUpdated += OnStateUpdated;
                _cytExpertAutomationEvent.TubeRecordResultGenerated += OnTubeRecordResultGenerated;
                // Console.WriteLine("Check event!");
            }

            int check1 = _cytExpertAutomation.Connect(60000, @"C:\Program Files\CytExpert\");
            Console.WriteLine(check1);
            while ((GlobalFlag.isServerReady & GlobalFlag.isInstrumentStandBy) == false) ;
            Console.WriteLine("Connection Successful!");

            string strFilePath = @"C:\my_git_repo\evotron\cytoflex\experiments\Exp_20210608_1.xit";            
            int check2 = _cytExpertAutomation.OpenExperiment(strFilePath);
            Console.WriteLine(check2);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;

            int check3 = _cytExpertAutomation.InitializeCytometer();
            Console.WriteLine(check3);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;

            int check4 = _cytExpertAutomation.EjectPlate();
            Console.WriteLine(check4);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;

            System.Threading.Thread.Sleep(5000);

            int check5 = _cytExpertAutomation.LoadPlate();
            Console.WriteLine(check5);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;

            string _plateID = "testID1234";
            string _plateName = "01";
            // string _xmlDesiredResult; // = "<?xml version="1.0"?> <CytExpertAutomation Revision="1.0"> <DesiredAcquisitionResults> </DesiredAcquisitionResults> </CytExpertAutomation>";
            string _xmlDesiredResult = System.IO.File.ReadAllText("C:/Users/santsa/Desktop/auto_sampler/cytoflex_control/test_xml_desired_result.xml");
            // Console.WriteLine(_xmlDesirecResult);
            int check6 =_cytExpertAutomation.AutoRecord(_plateID, _plateName, _xmlDesiredResult, out IEnumerable<string> _xsdErrorList);
            Console.WriteLine(check6);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;
            // Console.WriteLine(_xsdErrorList.ElementAt(0));


            // System.Threading.Thread.Sleep(10000);
            int check7 = _cytExpertAutomation.Disconnect();
            Console.WriteLine(check7);
            while (GlobalFlag.isActionComplete == false) ;
            GlobalFlag.isActionComplete = false;

            /*
                        int check4 = _cytExpertAutomation.EjectPlate();
                                    Console.WriteLine(check4);
                                    while (GlobalFlag.isActionComplete == false) ;
                                    GlobalFlag.isActionComplete = false;

                        System.Threading.Thread.Sleep(5000);

                                    int check5 = _cytExpertAutomation.LoadPlate();
                                    Console.WriteLine(check5);
                                    while (GlobalFlag.isActionComplete == false) ;
                                    GlobalFlag.isActionComplete = false;
              */

        }
    }
}
