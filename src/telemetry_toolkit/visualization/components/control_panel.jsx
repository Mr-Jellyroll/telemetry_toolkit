import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ArrowUp, ArrowDown, 
  PlaneTakeoff, PlaneLanding,
  RotateCcw, Power, 
  AlertTriangle
} from 'lucide-react';

const VehicleControlPanel = () => {
  // State for vehicle parameters
  const [altitude, setAltitude] = useState(100);
  const [speed, setSpeed] = useState(0);
  const [heading, setHeading] = useState(0);
  const [isEmergencyMode, setIsEmergencyMode] = useState(false);

  // Simulated battery level
  const [batteryLevel, setBatteryLevel] = useState(100);

  // Emergency mode handler
  const toggleEmergencyMode = () => {
    setIsEmergencyMode(!isEmergencyMode);
    if (!isEmergencyMode) {
      // Emergency protocol
      setSpeed(0);
      setAltitude(0);
    }
  };

  // Predefined flight patterns
  const takeoffSequence = () => {
    setAltitude(300);
    setSpeed(20);
    setHeading(0);
  };

  const landingSequence = () => {
    setSpeed(5);
    setAltitude(0);
  };

  return (
    <div className="w-full max-w-4xl p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Main Control Panel */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Flight Control System
              <div className="flex items-center gap-2">
                <span className={`h-3 w-3 rounded-full ${
                  batteryLevel > 20 ? 'bg-green-500' : 'bg-red-500'
                }`}></span>
                <span className="text-sm">{batteryLevel}% Battery</span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Emergency Mode Alert */}
            {isEmergencyMode && (
              <Alert variant="destructive" className="mb-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Emergency Mode Active - Initiating Safety Protocol
                </AlertDescription>
              </Alert>
            )}

            {/* Primary Controls */}
            <div className="space-y-6">
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
                    onValueChange={([value]) => setAltitude(value)}
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
                  onValueChange={([value]) => setSpeed(value)}
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
                    onValueChange={([value]) => setHeading(value)}
                    disabled={isEmergencyMode}
                  />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
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
    </div>
  );
};

export default VehicleControlPanel;