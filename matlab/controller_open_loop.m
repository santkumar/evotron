classdef controller_open_loop < handle
    
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
        
        function thisClass = controller_open_loop(thisClass)
            thisClass.totalNumSamples = 300;
            thisClass.ratioSetPoint = ones(1,thisClass.totalNumSamples);
            thisClass.kp = 5.9055e+03;
            thisClass.ki = 3.0382;
            thisClass.kd = 2.3427e+05;
            thisClass.kbc = 0.01;
            thisClass.photophillicStrainFraction = [];
            thisClass.constitutiveStrainFraction = [];
            thisClass.error = [];
            thisClass.integralValRaw = [];
            thisClass.backCalculation = [];
            thisClass.integralVal = [];
            thisClass.dt = 30;
            thisClass.controllerType = 'PID on error';
            thisClass.controlOutput = zeros(1,thisClass.totalNumSamples); % [0, 800]
            thisClass.maxLightIntensity = 800;
            thisClass.minLightIntensity = 0;
            thisClass.cytOutputPopulationName = 'V1R';
            thisClass.cytOutputSignalName = blanks(0); % for acquisition result data with no signal name, it is 1x0 empty char array 
            thisClass.iterationCount = 0;
        end
        
        function [] = updateController(thisClass, iteration, evolverExptDirectory, vial)
            
            measuredFraction = thisClass.extractStrainFraction(evolverExptDirectory, iteration, vial);
            thisClass.photophillicStrainFraction = [thisClass.photophillicStrainFraction, measuredFraction];
            
            output = thisClass.controlOutput(iteration);
                        
%             % Apply the computed output (light intensity)
%             thisClass.applyNewLightIntensity(output, evolverExptDirectory, vial)
            
            % Append variables
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