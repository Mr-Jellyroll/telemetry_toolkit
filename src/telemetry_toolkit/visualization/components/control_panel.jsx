import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ArrowUp, ArrowDown, 
  PlaneTakeoff, PlaneLanding,
  RotateCcw, Power, 
  AlertTriangle,
  Navigation
} from 'lucide-react';

const VehicleControlPanel = () => {
  // Flight control state
  const [altitude, setAltitude] = useState(100);
  const [speed, setSpeed] = useState(0);
  const [heading, setHeading] = useState(0);
  const [isEmergencyMode, setIsEmergencyMode] = useState(false);
  const [batteryLevel, setBatteryLevel] = useState(100);
  const [flightStatus, setFlightStatus] = useState('Ready');

  // Flight path presets
  const sanDiegoTour = async () => {
    setFlightStatus('Starting San Diego tour...');
    
    // Takeoff sequence
    await executeFlightStep('Taking off...', () => {
      setAltitude(300);
      setSpeed(20);
    });

    // Balboa Park
    await executeFlightStep('Flying to Balboa Park...', () => {
      setHeading(45);
    });

    // Circle Balboa Park
    for (let angle = 0; angle < 360; angle += 45) {
      await executeFlightStep('Circling Balboa Park...', () => {
        setHeading(angle);
      });
    }

    // USS Midway
    await executeFlightStep('Moving to USS Midway...', () => {
      setHeading(270);
    });

    // Coronado Bridge
    await executeFlightStep('Flying over Coronado Bridge...', () => {
      setHeading(225);
      setAltitude(200);
    });

    // Point Loma
    await executeFlightStep('Heading to Point Loma...', () => {
      setHeading(315);
      setAltitude(250);
    });

    // Return downtown
    await executeFlightStep('Returning downtown...', () => {
      setHeading(90);
      setSpeed(15);
    });

    // Landing sequence
    await executeFlightStep('Beginning final approach...', () => {
      setAltitude(100);
      setSpeed(5);
    });

    await executeFlightStep('Landing...', () => {
      setAltitude(0);
      setSpeed(0);
    });

    setFlightStatus('Tour completed');
  };

  // Helper function for flight steps
  const executeFlightStep = async (status, action) => {
    if (isEmergencyMode) return;
    setFlightStatus(status);
    action();
    await new Promise(resolve => setTimeout(resolve, 3000));
  };

  // Emergency protocols
  const toggleEmergencyMode = () => {
    setIsEmergencyMode(!isEmergencyMode);
    if (!isEmergencyMode) {
      setSpeed(0);
      setAltitude(0);
      setFlightStatus('EMERGENCY LANDING INITIATED');
    } else {
      setFlightStatus('Emergency mode cleared');
    }
  };

  // Standard flight sequences
  const takeoffSequence = () => {
    if (!isEmergencyMode) {
      setAltitude(300);
      setSpeed(20);
      setHeading(0);
      setFlightStatus('Executing takeoff sequence');
    }
  };

  const landingSequence = () => {
    if (!isEmergencyMode) {
      setSpeed(5);
      setAltitude(0);
      setFlightStatus('Executing landing sequence');
    }
  };

  // Battery simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setBatteryLevel(prev => {
        const drain = (speed * 0.01) + (altitude * 0.001);
        return Math.max(0, prev - drain);
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [speed, altitude]);

  return (
    <div className="w-full max-w-4xl p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Flight Control System
            <div className="flex items-center gap-2">
              <span className={`h-3 w-3 rounded-full ${
                batteryLevel > 20 ? 'bg-green-500' : 'bg-red-500'
              }`}></span>
              <span className="text-sm">{Math.round(batteryLevel)}% Battery</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isEmergencyMode && (
            <Alert variant="destructive" className="mb-4">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Emergency Mode Active - Initiating Safety Protocol
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-6">
            {/* Status Display */}
            <div className="text-sm font-medium text-gray-500">
              Status: {flightStatus}
            </div>

            {/* Altitude Control */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Target Altitude</span>
                <span className="text-sm text-gray-500">{altitude}m</span>
              </div>
              <div className="flex items-center gap-4">
                <ArrowDown className="h-4 w-4" />
                <Slider
                  value={[altitude]}
                  max={1000}
                  step={10}
                  className="flex-1"
                  onValueChange={([value]) => !isEmergencyMode && setAltitude(value)}
                  disabled={isEmergencyMode}
                />
                <ArrowUp className="h-4 w-4" />
              </div>
            </div>

            {/* Speed Control */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Target Speed</span>
                <span className="text-sm text-gray-500">{speed}m/s</span>
              </div>
              <Slider
                value={[speed]}
                max={50}
                step={1}
                className="flex-1"
                onValueChange={([value]) => !isEmergencyMode && setSpeed(value)}
                disabled={isEmergencyMode}
              />
            </div>

            {/* Heading Control */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Heading</span>
                <span className="text-sm text-gray-500">{heading}°</span>
              </div>
              <div className="flex items-center gap-4">
                <RotateCcw className="h-4 w-4" />
                <Slider
                  value={[heading]}
                  max={359}
                  step={5}
                  className="flex-1"
                  onValueChange={([value]) => !isEmergencyMode && setHeading(value)}
                  disabled={isEmergencyMode}
                />
                <Navigation className="h-4 w-4" />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2 mt-6">
            <Button
              variant="secondary"
              size="sm"
              onClick={takeoffSequence}
              disabled={isEmergencyMode}
            >
              <PlaneTakeoff className="h-4 w-4 mr-2" />
              Takeoff
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={landingSequence}
              disabled={isEmergencyMode}
            >
              <PlaneLanding className="h-4 w-4 mr-2" />
              Landing
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={sanDiegoTour}
              disabled={isEmergencyMode}
            >
              <Navigation className="h-4 w-4 mr-2" />
              San Diego Tour
            </Button>
            <Button
              variant={isEmergencyMode ? "destructive" : "outline"}
              size="sm"
              onClick={toggleEmergencyMode}
            >
              <Power className="h-4 w-4 mr-2" />
              {isEmergencyMode ? "Clear Emergency" : "Emergency Stop"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VehicleControlPanel;