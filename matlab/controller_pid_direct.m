classdef controller_pid_direct < handle
    
    properties
        totalNumSamples
        ratioSetPoint
        kp
        ki
        kd
        kbc
        photophillicStrainFraction
        constitutiveStrainFraction
        error
        integralValRaw
        backCalculation
        integralVal
        dt
        controllerType
        controlOutput
        maxLightIntensity
        minLightIntensity
        cytOutputPopulationName
        cytOutputSignalName
        iterationCount
    end % properties
    
    methods
        
        function thisClass = controller_pid_direct(thisClass)
            thisClass.totalNumSamples = 300;
            thisClass.ratioSetPoint = [0.4*ones(1,thisClass.totalNumSamples)];
% Parameters for co-cultures with bJAG235
%             thisClass.kp = 5.9055e+03;
%             thisClass.ki = 3.0382;
%             thisClass.kd = 2.3427e+05;
%             thisClass.kbc = 0.01;
% Parameters for co-cultures with bJAG237
            thisClass.kp = 1.5327e+03; % 5.9055e+03;
            thisClass.ki = 9.6743; % 3.0382;
            thisClass.kd = 95689; % 2.3427e+05;
            thisClass.kbc = 0.1;
            thisClass.photophillicStrainFraction = [];
            thisClass.constitutiveStrainFraction = [];
            thisClass.error = [];
            thisClass.integralValRaw = [];
            thisClass.backCalculation = [];
            thisClass.integralVal = [];
            thisClass.dt = 30;
            thisClass.controllerType = 'PID on error';
            thisClass.controlOutput = [0];
            thisClass.maxLightIntensity = 800;
            thisClass.minLightIntensity = 0;
            thisClass.cytOutputPopulationName = 'V1R';
            thisClass.cytOutputSignalName = blanks(0); % for acquisition result data with no signal name, it is 1x0 empty char array 
            thisClass.iterationCount = 0;
        end
        
        function [] = updateController(thisClass, iteration, evolverExptDirectory, vial)
            
            measuredFraction = thisClass.extractStrainFraction(evolverExptDirectory, iteration, vial);
            thisClass.photophillicStrainFraction = [thisClass.photophillicStrainFraction, measuredFraction];
            
            y_set = thisClass.ratioSetPoint(iteration);
            y_curr = thisClass.photophillicStrainFraction(end);
            
            if length(thisClass.photophillicStrainFraction) == 1
                y_prev = y_curr;
                e_curr = y_set - y_curr;
                fullIntegralVal = 0;
            else
                y_prev = thisClass.photophillicStrainFraction(end-1);
                e_curr = y_set - y_curr;
                fullIntegralVal = thisClass.integralVal(end);
            end
            
            switch thisClass.controllerType
                case 'PID on error'
                    %     P, I and D terms act on error
                    intTerm_raw = thisClass.ki*thisClass.dt*e_curr;
                    thisClass.integralValRaw = [thisClass.integralValRaw, intTerm_raw];
                    
                    intTerm = fullIntegralVal + intTerm_raw;
                    output_candidate = round(thisClass.kp*e_curr ...
                                                + intTerm ...
                                                + thisClass.kd*(y_prev-y_curr)/thisClass.dt);
                    if output_candidate > thisClass.maxLightIntensity
                        output = thisClass.maxLightIntensity;
                    elseif output_candidate < thisClass.minLightIntensity
                        output = thisClass.minLightIntensity;
                    else
                        output = output_candidate;
                    end
                    bc = output - output_candidate;
                    thisClass.backCalculation = [thisClass.backCalculation, bc];
                    intTerm = intTerm + thisClass.kbc*thisClass.ki*bc;
                    
%                 case 'PI on error, D on PV'
%                     %     D term act on process variable, P and I term acts on error
%                     output = thisClass.controlOutput(end) ...
%                                 + thisClass.kp*e(1) ...
%                                 + thisClass.kd/thisClass.dt*yHist(1) ...
%                                 - thisClass.kp*e(2) ...
%                                 - 2*thisClass.kd/thisClass.dt*yHist(2) ...
%                                 + thisClass.kd/thisClass.dt*yHist(3);
%                     
%                 case 'I on error, PD on PV'
%                     %     P and D terms act on process variable, I term acts on error
%                     output = thisClass.controlOutput(end) ...
%                                 + (thisClass.kp + thisClass.kd/thisClass.dt)*yHist(1) ...
%                                 + (-thisClass.kp - 2*thisClass.kd/thisClass.dt)*yHist(2) ...
%                                 + thisClass.kd/thisClass.dt*yHist(3);
%                 otherwise
%                     error(strcat('Unknown controller type: ', thisClass.controllerType));
            end
            
            % Apply the computed output (light intensity)
            thisClass.applyNewLightIntensity(output, evolverExptDirectory, vial)
            
            % Append variables
            thisClass.error = [thisClass.error, e_curr];
            thisClass.integralVal = [thisClass.integralVal, intTerm];
            if iteration==1
                thisClass.controlOutput = output;
            else
                thisClass.controlOutput = [thisClass.controlOutput, output];
            end
            thisClass.iterationCount = iteration;
            
        end
        
        function outputFraction = extractStrainFraction(thisClass, evolverExptDirectory, iteration, vial)
            
            vial = erase(vial, ["!" "?"]);
            acquisitionResultFile = strcat(evolverExptDirectory, '\sampling_results\vial_', vial, '_acquisition_result_', num2str(iteration), '.xml');
            resultStruct = xml2struct(acquisitionResultFile);
            numStats = numel(resultStruct.CytExpertAutomation.DesiredAcquisitionResult.Statistics.Statistic);
            for i=1:numStats
                population = resultStruct.CytExpertAutomation.DesiredAcquisitionResult.Statistics.Statistic{i}.Attributes.Population;
                signal = resultStruct.CytExpertAutomation.DesiredAcquisitionResult.Statistics.Statistic{i}.Attributes.Signal;
                if strcmp(population,thisClass.cytOutputPopulationName) & strcmp(signal,thisClass.cytOutputSignalName)
                    outputFraction = str2num(resultStruct.CytExpertAutomation.DesiredAcquisitionResult.Statistics.Statistic{i}.Attributes.Value);
                    break;
                end
                if i==numStats
                    error('Can not extract fraction from acquisition result file!')
                end
            end
            
        end
        
        function [] = applyNewLightIntensity(thisClass, lightIntensity, evolverExptDirectory, vial)
            
            vial = erase(vial, ["!" "?"]);
            vial = num2str(str2num(vial));
            ledIntensityFile = strcat(evolverExptDirectory, '\LED1_input\vial', vial, '_LED1_input.txt');
            fileID = fopen(ledIntensityFile,'at');
            fprintf(fileID,'%i,%u\n',-1,lightIntensity + 2050);
            fclose(fileID);
            
        end 
        
    end % methods
    
end % classdef