<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Mask Detection" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="QSTOMIT-MASQUE" src="resources/QSTOMIT-MASQUE.model" />
        <File name="deploy" src="resources/deploy.prototxt" />
        <File name="weights" src="resources/weights.caffemodel" />
        <File name="icon" src="icon.png" />
    </Resources>
    <Topics />
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
        <Translation name="translation_fr_FR" src="translations/translation_fr_FR.ts" language="fr_FR" />
    </Translations>
</Package>
