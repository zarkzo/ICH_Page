/**
 * ICH Detection System - ICH Type Information Modal
 * File: frontend/js/ich-modal.js
 * Handles clickable ICH type explanations with detailed medical information
 */

// Detailed ICH type information database
const ICH_INFO = {
  Intraparenchymal: {
    title: "Intraparenchymal Hemorrhage",
    definition:
      "Bleeding that occurs directly within the brain tissue (parenchyma), representing the most common form of spontaneous intracerebral hemorrhage.",
    causes: [
      "Chronic hypertension (most common cause, 50-60% of cases)",
      "Head trauma",
      "Cerebral amyloid angiopathy",
      "Arteriovenous malformation (AVM)",
      "Anticoagulant therapy complications",
      "Brain tumors",
      "Vasculitis",
      "Drug abuse (cocaine, amphetamines)",
    ],
    clinical:
      "Typically presents with sudden onset of focal neurological deficits depending on hemorrhage location. Common symptoms include headache, altered consciousness, nausea, vomiting, and seizures. Can cause increased intracranial pressure and mass effect leading to herniation.",
    importance:
      "Requires immediate medical attention and neuroimaging. The location, size, and patient's clinical condition determine treatment approach, which may include medical management, surgical evacuation, or minimally invasive procedures. Early detection is critical for reducing mortality and morbidity.",
    prevalence:
      "Most common type of spontaneous intracerebral hemorrhage, accounting for approximately 10-15% of all strokes. Has a 30-day mortality rate of about 35-52%.",
  },
  Intraventricular: {
    title: "Intraventricular Hemorrhage",
    definition:
      "Bleeding that occurs within the brain's ventricular system, the interconnected cavities where cerebrospinal fluid (CSF) is produced and circulates.",
    causes: [
      "Extension from intraparenchymal hemorrhage (most common)",
      "Primary intraventricular bleeding (rare, <5% of cases)",
      "Arteriovenous malformation rupture",
      "Aneurysm rupture",
      "Head trauma",
      "Coagulopathy",
      "Tumor hemorrhage",
      "Venous thrombosis",
    ],
    clinical:
      "Can obstruct cerebrospinal fluid flow, leading to acute hydrocephalus. Symptoms include sudden severe headache, altered level of consciousness, nausea, vomiting, and rapid neurological deterioration. May present with signs of increased intracranial pressure.",
    importance:
      "Carries high mortality rate (50-80%). May require urgent neurosurgical intervention including external ventricular drainage (EVD) to relieve hydrocephalus. Early detection and prompt treatment are critical for preventing complications from increased intracranial pressure and improving outcomes.",
    prevalence:
      "Occurs in about 40-50% of intraparenchymal hemorrhages as secondary extension. Primary IVH is rare. Presence of IVH significantly worsens prognosis of ICH.",
  },
  Subarachnoid: {
    title: "Subarachnoid Hemorrhage (SAH)",
    definition:
      "Bleeding in the subarachnoid space, the area between the arachnoid membrane and the pia mater containing cerebrospinal fluid and blood vessels.",
    causes: [
      "Ruptured cerebral aneurysm (80-85% of cases)",
      "Arteriovenous malformation (AVM)",
      "Head trauma (traumatic SAH)",
      "Bleeding disorders (hemophilia, thrombocytopenia)",
      "Blood vessel abnormalities",
      "Cocaine or amphetamine use",
      "Anticoagulation therapy",
      "Reversible cerebral vasoconstriction syndrome (RCVS)",
    ],
    clinical:
      'Classic presentation includes sudden "thunderclap" headache, often described as the worst headache of one\'s life with peak intensity within seconds. Associated symptoms may include neck stiffness (nuchal rigidity), photophobia, nausea, vomiting, altered consciousness, and focal neurological deficits. Sentinel headaches may occur days before rupture.',
    importance:
      "Medical and neurosurgical emergency requiring immediate evaluation and treatment. High risk of rebleeding (4% in first 24 hours, 20% in first 2 weeks) and delayed cerebral vasospasm (typically 3-14 days post-hemorrhage). Early diagnosis with CT angiography and securing of aneurysm (surgical clipping or endovascular coiling) is critical for survival and prevention of complications.",
    prevalence:
      "Accounts for 5-10% of all strokes. Aneurysmal SAH has mortality rate of 40-50%, with approximately 30% occurring before hospital arrival. Mean age of occurrence is 50-60 years, slightly more common in women.",
  },
  Subdural: {
    title: "Subdural Hemorrhage/Hematoma",
    definition:
      "Blood collection between the dura mater (outer meningeal layer) and the arachnoid mater (middle layer), typically resulting from tearing of bridging veins.",
    causes: [
      "Head trauma (most common, even minor in elderly)",
      "Falls (especially in elderly population)",
      "Anticoagulation or antiplatelet therapy",
      "Brain atrophy (creates space for blood accumulation)",
      "Chronic alcohol abuse",
      "Coagulopathy",
      "Birth trauma in neonates",
      "Rapid acceleration-deceleration injuries",
    ],
    clinical:
      "Can be acute (symptoms within 72 hours), subacute (3-21 days), or chronic (>21 days). Acute subdurals present with rapid neurological deterioration, headache, confusion, and decreased consciousness. Chronic subdurals may have insidious onset with subtle symptoms like personality changes, mild confusion, or gait disturbance. May present with focal neurological deficits.",
    importance:
      "Large acute subdurals may require emergency surgical evacuation (craniotomy or burr hole drainage). Chronic subdurals are particularly common in elderly patients, those on anticoagulants, and patients with brain atrophy. Treatment depends on size, symptoms, and rate of expansion. Without treatment, can cause brain herniation and death.",
    prevalence:
      "One of the most common types of intracranial injuries, with incidence increasing with age. Chronic subdurals have incidence of 1-2 per 100,000 in general population, rising to 7.4-8 per 100,000 in those over 70 years. Mortality for acute subdurals is 50-85%.",
  },
  Epidural: {
    title: "Epidural Hemorrhage/Hematoma",
    definition:
      "Blood collection between the skull (calvarium) and the outer layer of dura mater, typically from arterial bleeding following skull fracture.",
    causes: [
      "Skull fracture with arterial tear (typically middle meningeal artery)",
      "Severe head trauma",
      "Sports-related injuries",
      "Motor vehicle accidents",
      "Falls from height",
      "Rarely spontaneous in anticoagulated patients",
      "Birth trauma in neonates",
      "Venous bleeding (less common, better prognosis)",
    ],
    clinical:
      'Classic presentation (seen in <30% of cases) includes brief loss of consciousness, followed by a "lucid interval" of apparent recovery, then rapid deterioration with decreased consciousness, contralateral hemiparesis, and ipsilateral pupil dilation. However, many patients do not follow this classic pattern. Symptoms include severe headache, vomiting, seizures, and signs of increased intracranial pressure.',
    importance:
      "True neurosurgical emergency requiring immediate recognition and treatment. Rapid arterial bleeding can cause sudden increase in intracranial pressure and brain herniation. Excellent prognosis if diagnosed and treated promptly before herniation occurs (mortality <5%). Without treatment, mortality approaches 100%. Requires urgent craniotomy for hematoma evacuation.",
    prevalence:
      "Less common than subdural hematoma, accounting for about 2% of head injuries requiring hospitalization and 5-15% of fatal head injuries. Most common in young adults and adolescents. Peak incidence in second and third decades of life. With prompt surgical intervention, excellent recovery is possible.",
  },
};

class ICHModal {
  constructor() {
    this.modal = document.getElementById("ich-modal");
    this.modalTitle = document.getElementById("modal-title");
    this.modalBody = document.getElementById("modal-body");
    this.modalClose = document.getElementById("modal-close");

    this.init();
  }

  /**
   * Initialize modal functionality
   */
  init() {
    // Setup clickable ICH items
    const ichItems = document.querySelectorAll(".ich-info-item.clickable");
    ichItems.forEach((item) => {
      item.addEventListener("click", (e) => {
        const ichType = item.getAttribute("data-ich-type");
        this.showModal(ichType);
      });
    });

    // Setup close button
    if (this.modalClose) {
      this.modalClose.addEventListener("click", () => this.hideModal());
    }

    // Close when clicking outside modal content
    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.hideModal();
      }
    });

    // Close on ESC key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.modal.classList.contains("active")) {
        this.hideModal();
      }
    });

    console.log("ICH Modal initialized");
  }

  /**
   * Show modal with ICH type information
   */
  showModal(ichType) {
    const info = ICH_INFO[ichType];

    if (!info) {
      console.error("No information found for:", ichType);
      return;
    }

    // Set title
    this.modalTitle.textContent = info.title;

    // Build detailed content
    let content = `
            <h3>📋 Definition</h3>
            <p>${info.definition}</p>

            <h3>🔍 Common Causes</h3>
            <ul>
                ${info.causes.map((cause) => `<li>${cause}</li>`).join("")}
            </ul>

            <h3>🏥 Clinical Presentation</h3>
            <p>${info.clinical}</p>

            <h3>⚠️ Why Detection is Important</h3>
            <p>${info.importance}</p>

            <h3>📊 Epidemiology</h3>
            <p>${info.prevalence}</p>

            <div style="margin-top: 24px; padding: 16px; background: var(--bg-light); border-radius: 8px; border-left: 4px solid #f59e0b;">
                <p style="font-size: 14px; font-style: italic; margin: 0; line-height: 1.6;">
                    <strong>⚠️ Medical Disclaimer:</strong> This information is for educational and research purposes only. 
                    Diagnosis and treatment of intracranial hemorrhage should only be performed by qualified healthcare professionals. 
                    This AI system is not intended for clinical use or medical decision-making.
                </p>
            </div>
        `;

    this.modalBody.innerHTML = content;

    // Show modal with animation
    this.modal.classList.add("active");
    document.body.style.overflow = "hidden"; // Prevent background scrolling

    console.log("Modal opened for:", ichType);
  }

  /**
   * Hide modal
   */
  hideModal() {
    this.modal.classList.remove("active");
    document.body.style.overflow = ""; // Restore scrolling

    console.log("Modal closed");
  }
}

// Initialize modal when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.ichModal = new ICHModal();
});
