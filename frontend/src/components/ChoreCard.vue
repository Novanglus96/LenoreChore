<template>
  <!-- The card is an <article> with its own accessible name, so a screen
       reader can navigate the list by chore instead of hearing an unbroken run
       of unlabelled groups. -->
  <v-card
    class="lc-chore-card lc-lift"
    :class="{ 'lc-completing': isCompleting }"
    tag="article"
    :aria-label="cardLabel"
    :rounded="$vuetify.display.smAndDown ? 0 : 'lg'"
    :elevation="0"
    border
  >
    <!-- The area group's colour, as identity rather than as a surface. Text
         never sits on it, so its contrast is not load-bearing and users keep
         whatever colour they picked. -->
    <div
      class="lc-chore-card__stripe"
      :class="`bg-${groupColor}`"
      aria-hidden="true"
    ></div>

    <div class="lc-chore-card__body">
      <div class="d-flex align-start ga-3">
        <v-avatar
          size="40"
          class="lc-chore-card__area-icon flex-shrink-0"
          :class="`text-${groupColor}`"
          aria-hidden="true"
        >
          <v-icon :icon="localchore.area.area_icon" size="22"></v-icon>
        </v-avatar>

        <div class="flex-grow-1 min-width-0">
          <h3 class="text-subtitle-1 font-weight-medium lc-chore-card__title">
            {{ localchore.chore_name }}
          </h3>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ localchore.area.area_name }}
            <span class="lc-visually-hidden">
              in {{ groupName }}</span
            >
          </p>
        </div>

        <!-- Due state. Overdue is carried by the word "overdue", an icon and a
             slow pulse -- not by red text alone, which is invisible to anyone
             who cannot distinguish it. -->
        <div v-if="localchore.status == 0" class="text-right flex-shrink-0">
          <v-chip
            size="small"
            :color="localchore.isOverdue ? 'filthy' : undefined"
            :variant="localchore.isOverdue ? 'flat' : 'tonal'"
            :class="{ 'lc-breathe': localchore.isOverdue }"
          >
            <v-icon
              start
              size="14"
              :icon="localchore.isOverdue ? 'mdi-alert-circle' : 'mdi-clock-outline'"
              aria-hidden="true"
            ></v-icon>
            {{ dueLabel }}
          </v-chip>
        </div>
      </div>

      <!-- Dirtiness. The percentage is spoken by the progressbar role, and the
           band name ("filthy") is redundant text so the meaning does not depend
           on the bar's colour. -->
      <div v-if="localchore.status == 0" class="mt-3">
        <v-progress-linear
          :model-value="localchore.dirtiness"
          :color="dirtBand.color"
          height="22"
          rounded
          :striped="localchore.dirtiness > 0"
          :aria-label="`${Math.ceil(localchore.dirtiness)} percent dirty, ${dirtBand.label}`"
        >
          <span class="text-caption font-weight-medium">
            {{ Math.ceil(localchore.dirtiness) }}% · {{ dirtBand.label }}
          </span>
        </v-progress-linear>
      </div>

      <v-alert
        v-else-if="localchore.status == 3"
        type="info"
        density="compact"
        class="mt-3"
        icon="mdi-island"
        text="Vacation mode — this chore is paused."
      ></v-alert>

      <div class="d-flex align-center justify-space-between mt-3 ga-2">
        <!-- Claiming used to be an unlabelled clipboard icon four buttons
             along the action bar, while the chip that named the assignee sat
             here doing nothing. The action now lives on the thing it changes.

             A v-btn rather than a clickable v-chip: the global VBtn default is
             already a pill, so it reads the same, and a button is focusable and
             operable by keyboard without any of it having to be hand-rolled. -->
        <v-btn
          class="lc-chore-card__assignee"
          size="small"
          variant="tonal"
          :color="localchore.isAssigned ? 'primary' : undefined"
          :prepend-icon="
            localchore.assignee ? 'mdi-account-check' : 'mdi-account-outline'
          "
          :aria-label="claimLabel"
          :aria-pressed="localchore.isAssigned ? 'true' : 'false'"
          :disabled="localchore.status > 0"
          @click="callClaimChore(localchore.id, localchore.assignee_id)"
        >
          {{ computedAssignee }}
        </v-btn>

        <!-- Display only, and now honestly so. These were `:readonly="!expand"`
             -- a control that looked live on a collapsed card and silently did
             nothing. Effort is a setting, so it is set in the editor. -->
        <div class="d-flex align-center ga-1">
          <span class="lc-visually-hidden">
            Effort: {{ effortLabel(localchore.effort) }}
          </span>
          <v-rating
            :model-value="localchore.effort"
            readonly
            length="3"
            size="18"
            density="compact"
            active-color="accent"
            aria-hidden="true"
          ></v-rating>
        </div>
      </div>

      <!-- The one fact the history panel existed to show. It was behind a
           button, in a table, in a second expanding panel; it is one line. -->
      <p class="text-caption text-medium-emphasis mb-0 mt-2">
        {{ lastDoneLabel }}
      </p>
    </div>

    <v-divider></v-divider>

    <!-- One primary action, one secondary, and everything else behind a menu
         whose items have names in words.
         ─────────────────────────────────────────────────────────────────────
         This was six icon buttons whose only labels were tooltips, which a
         touch device never shows -- and four of them greyed out whenever the
         inline editor was open, for reasons the screen never gave. -->
    <v-card-actions class="lc-chore-card__actions">
      <v-btn
        variant="flat"
        color="primary"
        size="small"
        prepend-icon="mdi-check"
        :aria-label="`Mark ${localchore.chore_name} complete`"
        :disabled="localchore.status > 0 || isCompleting"
        @click="callCompleteChore(localchore.id, getID)"
      >
        Done
      </v-btn>

      <v-btn
        variant="text"
        size="small"
        prepend-icon="mdi-alarm-snooze"
        :aria-label="`Snooze ${localchore.chore_name}`"
        :disabled="localchore.status > 0"
        @click="openSnooze()"
      >
        Snooze
      </v-btn>

      <v-spacer></v-spacer>

      <LcActionMenu
        :items="menuItems"
        :title="localchore.chore_name"
        @select="onMenuSelect"
      >
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            icon="mdi-dots-vertical"
            :aria-label="`More actions for ${localchore.chore_name}`"
          >
            <v-icon icon="mdi-dots-vertical"></v-icon>
          </v-btn>
        </template>
      </LcActionMenu>
    </v-card-actions>

    <!-- ── Overlays ────────────────────────────────────────────────────────
         All three are overlays rather than panels that grow the card. Nothing
         on this card changes height any more, so a list of them stays where it
         was when you last looked at it. -->
    <ChoreEditDialog
      v-model="editOpen"
      :chore="localchore"
      :remote-update-pending="remoteUpdatePending"
      @dirty="editDirty = true"
      @submit="callSaveChore"
      @cancel="cancelEdit"
    />

    <v-dialog v-model="snooze" scrollable max-width="420px">
      <v-card>
        <v-card-title>Snooze {{ localchore.chore_name }}</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <!-- VueDatePicker does not render an element carrying the id its
               `uid` prop implies, so a <label for> would point at nothing.
               Labelling the group is what actually reaches the control. -->
          <div
            :id="snoozeLabelId"
            class="text-body-2 mb-2"
            aria-hidden="true"
          >
            Push the due date to
          </div>
          <div role="group" :aria-labelledby="snoozeLabelId">
            <VueDatePicker
              v-model="snoozeDate"
              :timezone="userTimezone"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              teleport
              format="yyyy-MM-dd"
            ></VueDatePicker>
          </div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="snooze = false">Cancel</v-btn>
          <v-btn
            variant="flat"
            color="primary"
            @click="callSnoozeChore(localchore.id, snoozeDate)"
          >
            Snooze
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="historyOpen" scrollable max-width="420px">
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium">
          History for {{ localchore.chore_name }}
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-table v-if="localchore.last_three_history_items?.length">
            <thead>
              <tr>
                <th class="text-left">Date</th>
                <th class="text-left">Completed By</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in localchore.last_three_history_items"
                :key="`${item.completed_date}-${item.completed_by}`"
              >
                <td>{{ item.completed_date }}</td>
                <td>{{ item.completed_by }}</td>
              </tr>
            </tbody>
          </v-table>
          <p v-else class="text-body-2 text-medium-emphasis mb-0">
            This chore has never been completed.
          </p>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="historyOpen = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <LcConfirmDialog
      v-model="deleteDialog"
      title="Delete this chore?"
      icon="mdi-delete-forever-outline"
      confirm-label="Delete chore"
      confirm-icon="mdi-delete-forever-outline"
      @confirm="callDeleteChore(localchore)"
    >
      Deleting <strong>{{ localchore.chore_name }}</strong> from
      <strong>{{ localchore.area.area_name }}</strong> also removes it from the
      history. This cannot be undone.
    </LcConfirmDialog>
  </v-card>
</template>
<script setup>
// defineProps/defineEmits are compiler macros — importing them warns on every
// build and every test run.
import { computed, ref, watch, onMounted } from "vue";
import VueDatePicker from "@vuepic/vue-datepicker";
import { useUserStore } from "@/stores/user";
import { useOptions } from "@/composables/optionsComposable";
import { effortLabel } from "@/utils/labels";
import LcActionMenu from "@/components/LcActionMenu.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";
import ChoreEditDialog from "@/components/ChoreEditDialog.vue";

// Was hardcoded to "America/New_York", so every date this card wrote was
// interpreted in Eastern time regardless of where the user actually is --
// while the backend has stored a per-user notify_timezone since the reminders
// feature shipped. Falls back to the browser's own zone.
const userTimezone =
  Intl.DateTimeFormat().resolvedOptions().timeZone || undefined;

const { options } = useOptions();
const snooze = ref(false);
// Its own value rather than a v-model straight onto localchore.nextDue: the
// picker writes on every change, so picking a date and then pressing Cancel
// left the card showing a due date the server had never been told about.
const snoozeDate = ref(null);
const historyOpen = ref(false);
const editOpen = ref(false);
const deleteDialog = ref(false);
const userstore = useUserStore();
const emit = defineEmits([
  "editChore",
  "removeChore",
  "snoozeChore",
  "completeChore",
  "claimChore",
  "toggleActivation",
]);
const props = defineProps({
  chore: Object,
});
const localchore = ref({ ...props.chore });

// A grid mounts many of these; a literal id would make every snooze dialog's
// aria-labelledby point at the first card's label.
const snoozeLabelId = computed(() => `snooze-date-${props.chore?.id}`);

function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj));
}

// True while the editor holds changes the user has not saved. This was
// `saveEnabled`, which did double duty as "the Save button is live" and "hold
// remote updates back" -- and, fatally, as "disable the button that closes the
// editor". It only means the second thing now.
const editDirty = ref(false);

// True when a newer version of this chore arrived from the server while the
// user had unsaved edits, so we declined to apply it.
const remoteUpdatePending = ref(false);

watch(
  () => props.chore,
  updatedChore => {
    // Never overwrite unsaved edits. Every write endpoint publishes an SSE
    // event, so any other household member completing a chore invalidates
    // ["chores"] and hands this component a new object identity. Before this
    // guard that replaced the open editor's contents mid-typing -- and
    // because the dirty flag stayed set, the next click of Save wrote the
    // reverted values back over the server's copy.
    if (editDirty.value) {
      remoteUpdatePending.value = true;
      return;
    }
    localchore.value = deepCopy(updatedChore);
    remoteUpdatePending.value = false;
  },
);

onMounted(() => {
  localchore.value = deepCopy(props.chore);
});

// ── The overflow menu ───────────────────────────────────────────────────────
// Built as data rather than as markup so the mobile bottom sheet and the
// desktop menu cannot drift, and so "why is this greyed out" is answerable in
// the item itself rather than by reading a disabled expression in the template.
const menuItems = computed(() => {
  const c = localchore.value;
  const paused = c?.status == 3;
  return [
    {
      key: "edit",
      title: "Edit chore…",
      icon: "mdi-pencil-outline",
      disabled: paused,
      subtitle: paused ? "Paused for vacation" : undefined,
    },
    {
      key: "history",
      title: "Recent history",
      icon: "mdi-clipboard-text-clock-outline",
    },
    {
      key: "toggle",
      title: c?.status == 0 ? "Disable chore" : "Enable chore",
      icon: c?.status == 0 ? "mdi-circle-off-outline" : "mdi-circle-outline",
      disabled: paused,
      subtitle: paused ? "Paused for vacation" : undefined,
    },
    {
      key: "delete",
      title: "Delete chore",
      icon: "mdi-delete-forever-outline",
      color: "filthy",
      dividerBefore: true,
    },
  ];
});

const onMenuSelect = key => {
  if (key === "edit") editOpen.value = true;
  else if (key === "history") historyOpen.value = true;
  else if (key === "toggle")
    callToggleChore(localchore.value.id, localchore.value.status);
  else if (key === "delete") deleteDialog.value = true;
};

const getID = computed(() => {
  return userstore.getID;
});
const openSnooze = () => {
  snoozeDate.value = localchore.value.nextDue;
  snooze.value = true;
};

const callSnoozeChore = async (chore_id, next_due) => {
  emit("snoozeChore", chore_id, next_due);
  snooze.value = false;
};

// Cancel is what Reset used to be: discard the draft and show the server's
// current copy. It takes a full snapshot rather than restoring the nine fields
// the old Reset named individually -- that list omitted anything a remote
// change might have touched, assignee and status among them, which mattered
// precisely because the watch above holds updates back.
const cancelEdit = () => {
  localchore.value = deepCopy(props.chore);
  editDirty.value = false;
  remoteUpdatePending.value = false;
};

const callSaveChore = async saveChore => {
  editDirty.value = false;
  // Cleared explicitly rather than waiting for the post-save refetch to do it,
  // so the flag cannot outlive the edit it belongs to.
  remoteUpdatePending.value = false;
  localchore.value = deepCopy(saveChore);
  emit("editChore", saveChore);
};
const callDeleteChore = async deleteChore => {
  emit("removeChore", deleteChore);
  // Explicit rather than a toggle: LcConfirmDialog leaves closing to the
  // consumer, and a toggle here would reopen the dialog if it were ever called
  // from anywhere but the open one.
  deleteDialog.value = false;
};
// ── The completion moment ───────────────────────────────────────────────────
// The payoff beat of the app. The card lifts, springs away and fades while the
// dirtiness bar drains, and only then does the mutation fire.
//
// Ordering it that way is deliberate. The parent's optimistic update removes
// this chore from the list the instant the mutation starts, which unmounts the
// component -- so emitting first means the animation never renders at all.
// Waiting ~620ms before a chore completion costs nothing and is what makes the
// moment land rather than feel like a spinner.
//
// Under prefers-reduced-motion the wait collapses to zero along with the
// animation, so nobody who has asked for less motion pays a delay for it.
const isCompleting = ref(false);

const prefersReducedMotion = () =>
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const callCompleteChore = async (chore_id, user_id) => {
  if (isCompleting.value) return; // a second click would emit twice
  isCompleting.value = true;

  // Drain the bar in step with the card leaving.
  localchore.value.dirtiness = 0;

  const beat = prefersReducedMotion() ? 0 : 620; // keep in step with --lc-dur-celebrate
  if (beat) await new Promise(resolve => setTimeout(resolve, beat));

  emit("completeChore", chore_id, user_id);
};
const callClaimChore = async (chore_id, user_id) => {
  let assignee = null;
  if (getID.value == user_id) {
    assignee = null;
  } else {
    assignee = getID.value;
  }
  emit("claimChore", chore_id, assignee);
};
const callToggleChore = async (chore_id, active) => {
  emit("toggleActivation", chore_id, active);
};
// The dirtiness band, carrying BOTH a colour and a word. Colour alone was the
// only signal before, which fails for anyone who cannot distinguish the hues --
// and the thresholds are user-configurable, so the word is also the only thing
// that explains why a given percentage is "filthy" in this household.
// AreaOut.group is Optional now, matching the nullable column it maps -- an
// area can legitimately have no group. Dereferencing it blindly here would just
// move the crash from the API to the client.
const groupColor = computed(
  () => localchore.value?.area?.group?.group_color || "outline"
);
const groupName = computed(
  () => localchore.value?.area?.group?.group_name || "no group"
);

const dirtBand = computed(() => {
  const dirt = localchore.value?.dirtiness ?? 0;
  const med = options.value?.med_thresh ?? 49;
  const high = options.value?.high_thresh ?? 74;

  if (dirt <= med) return { color: "clean", label: "clean-ish" };
  if (dirt <= high) return { color: "soiled", label: "getting there" };
  return { color: "filthy", label: "filthy" };
});

const dueLabel = computed(() => {
  const days = localchore.value?.duedays ?? 0;
  if (days < 0) {
    const overdue = Math.abs(days);
    return `${overdue} day${overdue === 1 ? "" : "s"} overdue`;
  }
  if (days === 0) return "Due today";
  if (days === 1) return "Due tomorrow";
  return `Due in ${days} days`;
});

/**
 * The most recent completion, in words.
 *
 * Split rather than handed to `new Date(string)`: an ISO date with no time is
 * parsed as UTC midnight, so anywhere west of Greenwich it renders as the day
 * before -- which on a chore app means the card disagrees with the history
 * table about when you did something.
 */
const lastDoneLabel = computed(() => {
  const item = localchore.value?.last_three_history_items?.[0];
  if (!item) return "Never completed";

  const [y, m, d] = String(item.completed_date).split("-").map(Number);
  const when = new Date(y, (m || 1) - 1, d || 1).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
  });

  return item.completed_by
    ? `Last done ${when} by ${item.completed_by}`
    : `Last done ${when}`;
});

// State-dependent labels, so what a screen reader announces changes with the
// control rather than describing only its resting state.
const claimLabel = computed(() =>
  localchore.value?.isAssigned
    ? `Release ${localchore.value.chore_name}`
    : `Claim ${localchore.value?.chore_name}`
);

// The card's own accessible name, so the list can be navigated chore by chore.
const cardLabel = computed(() => {
  const c = localchore.value;
  if (!c) return "Chore";
  return `${c.chore_name}, ${c.area?.area_name}, ${Math.ceil(
    c.dirtiness
  )} percent dirty, ${dueLabel.value}`;
});

const computedAssignee = computed(() => {
  if (!localchore.value) {
    return "";
  }
  if (!localchore.value.assignee_id) {
    return "Unassigned";
  }
  if (!localchore.value.assignee.fullname) {
    return localchore.value.assignee.email;
  } else {
    if (localchore.value.assignee.fullname == " ") {
      return localchore.value.assignee.email;
    } else {
      return localchore.value.assignee.fullname;
    }
  }
});
</script>
<style scoped>
.lc-chore-card {
  position: relative;
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
}

/* The area group's colour, at the same width as the area card's -- they sit on
   the same screens and a 4px stripe beside a 6px one read as a mistake. Wide
   enough to identify at a glance in a scrolling list without becoming a block
   of colour competing with the content. */
.lc-chore-card__stripe {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: var(--lc-card-stripe);
}

.lc-chore-card__body {
  /* Clears the stripe so text never sits against it. */
  padding: var(--lc-space-4) var(--lc-space-4) var(--lc-space-3)
    calc(var(--lc-space-4) + var(--lc-card-stripe));
}

.lc-chore-card__area-icon {
  background: rgb(var(--v-theme-surface-variant));
}

/* Long chore names wrap rather than pushing the due chip off the card. */
.lc-chore-card__title {
  line-height: 1.3;
  overflow-wrap: anywhere;
}

/* A long name or email would otherwise push the effort stars off the card.
   The ellipsis has to go on .v-btn__content: that is the flex child holding
   the text, and clipping the button itself would just hide the overflow with
   no indication anything had been cut. */
.lc-chore-card__assignee {
  min-width: 0;
  max-width: 60%;
  text-transform: none;
  letter-spacing: normal;
}

.lc-chore-card__assignee :deep(.v-btn__content) {
  min-width: 0;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.min-width-0 {
  /* Flex children default to min-width:auto, which stops them shrinking below
     their content and is what lets a long word overflow the card. */
  min-width: 0;
}

.lc-chore-card__actions {
  padding-inline: var(--lc-space-2);
  gap: var(--lc-space-1);
}

@media (max-width: 599px) {
  .lc-chore-card__body {
    padding: var(--lc-space-3) var(--lc-space-3) var(--lc-space-2)
      calc(var(--lc-space-3) + var(--lc-card-stripe));
  }
}
</style>
