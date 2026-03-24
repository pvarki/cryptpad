import { useState } from "react";
import {
  ExternalLink,
  FileText,
  KanbanSquare,
  Presentation,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { OnboardingGuide } from "@/components/OnboardingGuide";
import { FeatureGuide } from "@/components/FeatureGuide";
import { Toaster } from "@/components/ui/sonner";
import { useTranslation } from "react-i18next";
import { PRODUCT_SHORTNAME } from "@/App";
import { useMeta } from "@/lib/metadata";
import { buildLoginUrl, type CryptPadCardData } from "@/lib/metadata";

interface FeatureStepDef {
  id: string;
  title: string;
  description: string;
  image: string;
  mobileImage?: string;
}

function getFeatureSteps(featureKey: string, theme: string): FeatureStepDef[] {
  const basePath = `/ui/cryptpad/assets/features/${featureKey}`;
  const steps: Record<string, FeatureStepDef[]> = {
    docs: [
      {
        id: "docs_intro",
        title: "features.docs.steps.intro.title",
        description: "features.docs.steps.intro.description",
        image: `${basePath}/${theme}/FEATURE_DOCS_INTRO.png`,
      },
      {
        id: "docs_create",
        title: "features.docs.steps.create.title",
        description: "features.docs.steps.create.description",
        image: `${basePath}/${theme}/FEATURE_DOCS_CREATE.png`,
      },
      {
        id: "docs_collaborate",
        title: "features.docs.steps.collaborate.title",
        description: "features.docs.steps.collaborate.description",
        image: `${basePath}/${theme}/FEATURE_DOCS_COLLABORATE.png`,
      },
      {
        id: "docs_share",
        title: "features.docs.steps.share.title",
        description: "features.docs.steps.share.description",
        image: `${basePath}/${theme}/FEATURE_DOCS_SHARE.png`,
      },
    ],
    kanban: [
      {
        id: "kanban_intro",
        title: "features.kanban.steps.intro.title",
        description: "features.kanban.steps.intro.description",
        image: `${basePath}/${theme}/FEATURE_KANBAN_INTRO.png`,
      },
      {
        id: "kanban_create",
        title: "features.kanban.steps.create.title",
        description: "features.kanban.steps.create.description",
        image: `${basePath}/${theme}/FEATURE_KANBAN_CREATE.png`,
      },
      {
        id: "kanban_manage",
        title: "features.kanban.steps.manage.title",
        description: "features.kanban.steps.manage.description",
        image: `${basePath}/${theme}/FEATURE_KANBAN_MANAGE.png`,
      },
    ],
    presentations: [
      {
        id: "pres_intro",
        title: "features.presentations.steps.intro.title",
        description: "features.presentations.steps.intro.description",
        image: `${basePath}/${theme}/FEATURE_PRES_INTRO.png`,
      },
      {
        id: "pres_create",
        title: "features.presentations.steps.create.title",
        description: "features.presentations.steps.create.description",
        image: `${basePath}/${theme}/FEATURE_PRES_CREATE.png`,
      },
      {
        id: "pres_present",
        title: "features.presentations.steps.present.title",
        description: "features.presentations.steps.present.description",
        image: `${basePath}/${theme}/FEATURE_PRES_PRESENT.png`,
      },
    ],
    unitUse: [
      {
        id: "unit_intro",
        title: "features.unitUse.steps.intro.title",
        description: "features.unitUse.steps.intro.description",
        image: `${basePath}/${theme}/FEATURE_UNIT_INTRO.png`,
      },
      {
        id: "unit_ops",
        title: "features.unitUse.steps.ops.title",
        description: "features.unitUse.steps.ops.description",
        image: `${basePath}/${theme}/FEATURE_UNIT_OPS.png`,
      },
      {
        id: "unit_secure",
        title: "features.unitUse.steps.secure.title",
        description: "features.unitUse.steps.secure.description",
        image: `${basePath}/${theme}/FEATURE_UNIT_SECURE.png`,
      },
    ],
  };

  return steps[featureKey] || [];
}

interface HomePageProps {
  data: CryptPadCardData;
}

export const HomePage = ({ data }: HomePageProps) => {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const meta = useMeta();
  const loginUrl = buildLoginUrl(data.url);

  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  const featureButtons = [
    {
      key: "docs",
      icon: FileText,
      label: "features.docs.title",
    },
    {
      key: "kanban",
      icon: KanbanSquare,
      label: "features.kanban.title",
    },
    {
      key: "presentations",
      icon: Presentation,
      label: "features.presentations.title",
    },
    {
      key: "unitUse",
      icon: Users,
      label: "features.unitUse.title",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Launch CryptPad Button */}
      <div className="flex justify-center">
        <a
          href={loginUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full"
        >
          <Button
            variant="outline"
            size="lg"
            className="w-full py-10 cursor-pointer text-lg font-bold gap-3 border-2 hover:border-primary/50 transition-all"
          >
            <img
              src="/ui/cryptpad/assets/cryptpad-mark.svg"
              alt=""
              aria-hidden="true"
              className="w-8 h-8"
            />
            {t("home.launch")}
            <ExternalLink className="w-5 h-5 ml-1" />
          </Button>
        </a>
      </div>

      {/* How to use CryptPad's features */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">
          {t("home.featuresTitle")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {featureButtons.map(({ key, icon: Icon, label }) => (
            <Button
              key={key}
              variant="outline"
              size="lg"
              className="w-full py-6 cursor-pointer justify-start gap-3"
              onClick={() => setActiveFeature(key)}
            >
              <Icon className="w-5 h-5 text-primary" />
              {t(label)}
            </Button>
          ))}
        </div>
      </div>

      {/* Feature Guide Drawers */}
      {featureButtons.map(({ key }) => (
        <FeatureGuide
          key={key}
          featureKey={key}
          steps={getFeatureSteps(key, meta.theme)}
          open={activeFeature === key}
          onOpenChange={(open) => {
            if (!open) setActiveFeature(null);
          }}
        />
      ))}

      <OnboardingGuide />
      <Toaster position="top-center" />
    </div>
  );
};
