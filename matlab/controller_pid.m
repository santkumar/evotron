classdef controller_pid < handle
    
    properties
        totalNumSamples
        ratioSetPoint
        kp
        ki
        kd
        photophillicStrainFraction
        constitutiveStrainFraction
        error
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
        
        function thisClass = controller_pid(thisClass)
            thisClass.totalNumSamples = 120;
            thisClass.ratioSetPoint = [0.4*ones(1,thisClass.totalNumSamples)];
            thisClass.kp = 1.5327e+03;
            thisClass.ki = 9.6743;
            thisClass.kd = 9.5689e+04;
            thisClass.photophillicStrainFraction = [];
            thisClass.constitutiveStrainFraction = [];
            thisClass.error = [];
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
            
            e = zeros(1,3);
            yHist = zeros(1,3);
            
            switch length(thisClass.photophillicStrainFraction)
                case 1
                    e(1) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end);
                    e(2) = e(1);
                    e(3) = e(1);
                    yHist(1) = thisClass.photophillicStrainFraction(end);
                    yHist(2) = thisClass.photophillicStrainFraction(end);
                    yHist(3) = thisClass.photophillicStrainFraction(end);
                case 2
                    e(1) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end);
                    e(2) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end-1);
                    e(3) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end-1);
                    yHist(1) = thisClass.photophillicStrainFraction(end);
                    yHist(2) = thisClass.photophillicStrainFraction(end-1);
                    yHist(3) = thisClass.photophillicStrainFraction(end-1);
                otherwise
                    e(1) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end);
                    e(2) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end-1);
                    e(3) = thisClass.ratioSetPoint(iteration) - thisClass.photophillicStrainFraction(end-2);                    
                    yHist(1) = thisClass.photophillicStrainFraction(end);
                    yHist(2) = thisClass.photophillicStrainFraction(end-1);
                    yHist(3) = thisClass.photophillicStrainFraction(end-2);
            end
            
            switch thisClass.controllerType
                case 'PID on error'
                    %     P, I and D terms act on error
                    output = thisClass.controlOutput(end) ...
                                + (thisClass.kp + thisClass.kd/thisClass.dt)*e(1) ...
                                + (-thisClass.kp - 2*thisClass.kd/thisClass.dt)*e(2) ...
                                + thisClass.kd/thisClass.dt*e(3);
                    
                case 'PI on error, D on PV'
                    %     D term act on process variable, P and I term acts on error
                    output = thisClass.controlOutput(end) ...
                                + thisClass.kp*e(1) ...
                                + thisClass.kd/thisClass.dt*yHist(1) ...
                                - thisClass.kp*e(2) ...
                                - 2*thisClass.kd/thisClass.dt*yHist(2) ...
                                + thisClass.kd/thisClass.dt*yHist(3);
                    
                case 'I on error, PD on PV'
                    %     P and D terms act on process variable, I term acts on error
                    output = thisClass.controlOutput(end) ...
                                + (thisClass.kp + thisClass.kd/thisClass.dt)*yHist(1) ...
                                + (-thisClass.kp - 2*thisClass.kd/thisClass.dt)*yHist(2) ...
                                + thisClass.kd/thisClass.dt*yHist(3);
                otherwise
                    error(strcat('Unknown controller type: ', thisClass.controllerType));
            end
            
            % Add integral term and check bound on output
            intTerm = thisClass.ki*thisClass.dt*e(1);
            output = round(output + intTerm);
            if output > thisClass.maxLightIntensity
                output = thisClass.maxLightIntensity;
            elseif output < thisClass.minLightIntensity
                output = thisClass.minLightIntensity;
            end
            
            % Apply the computed output (light intensity)
            thisClass.applyNewLightIntensity(output, evolverExptDirectory, vial)
            
            % Append variables
            thisClass.error = [thisClass.error, e(1)];
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