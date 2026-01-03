'use client';

import { useState } from 'react';
import { Button } from '../ui/button';

interface PreferenceQuestion {
  id: string;
  question: string;
  options: { value: string; label: string; description?: string }[];
}

interface PreferenceWizardProps {
  questions: PreferenceQuestion[];
  onComplete: (answers: Record<string, string>) => void;
  onBack?: () => void;
}

export function PreferenceWizard({ questions, onComplete, onBack }: PreferenceWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const currentQuestion = questions[currentStep];
  const isLastStep = currentStep === questions.length - 1;
  const progress = ((currentStep + 1) / questions.length) * 100;

  const handleSelect = (value: string) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
  };

  const handleNext = () => {
    if (isLastStep) {
      onComplete(answers);
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep === 0 && onBack) {
      onBack();
    } else {
      setCurrentStep((prev) => Math.max(0, prev - 1));
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-xs text-muted mb-2">
          <span>Step {currentStep + 1} of {questions.length}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-1 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <h3 className="text-lg font-medium mb-6">{currentQuestion.question}</h3>

      {/* Options */}
      <div className="space-y-3 mb-8">
        {currentQuestion.options.map((option) => (
          <button
            key={option.value}
            onClick={() => handleSelect(option.value)}
            className={`w-full text-left p-4 rounded-lg border transition-all ${
              answers[currentQuestion.id] === option.value
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            }`}
          >
            <div className="font-medium">{option.label}</div>
            {option.description && (
              <div className="text-sm text-muted mt-1">{option.description}</div>
            )}
          </button>
        ))}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="ghost" onClick={handlePrev}>
          Back
        </Button>
        <Button
          onClick={handleNext}
          disabled={!answers[currentQuestion.id]}
        >
          {isLastStep ? 'Complete' : 'Next'}
        </Button>
      </div>
    </div>
  );
}

// Default preference questions for brainstorming
export const defaultPreferenceQuestions: PreferenceQuestion[] = [
  {
    id: 'risk_tolerance',
    question: 'What is your risk tolerance for this project?',
    options: [
      { value: 'low', label: 'Conservative', description: 'Prefer proven approaches with minimal risk' },
      { value: 'medium', label: 'Balanced', description: 'Open to some risk for better outcomes' },
      { value: 'high', label: 'Aggressive', description: 'Willing to take significant risks for innovation' },
    ],
  },
  {
    id: 'time_priority',
    question: 'How important is implementation speed?',
    options: [
      { value: 'fast', label: 'Speed First', description: 'Need results as quickly as possible' },
      { value: 'balanced', label: 'Balanced', description: 'Balance between speed and quality' },
      { value: 'quality', label: 'Quality First', description: 'Take time to ensure best outcome' },
    ],
  },
  {
    id: 'innovation_level',
    question: 'How innovative should the solutions be?',
    options: [
      { value: 'conventional', label: 'Conventional', description: 'Stick to established methods' },
      { value: 'moderate', label: 'Moderate Innovation', description: 'Some new ideas, mostly proven' },
      { value: 'breakthrough', label: 'Breakthrough', description: 'Prioritize novel and creative solutions' },
    ],
  },
];
